"""测试真实网关适配协议，不向外部发送短信。"""

import json
import unittest
from unittest.mock import patch
import httpx
from fastapi import HTTPException
from pydantic import SecretStr
from app.core.config import Settings
from app.services.sms import HttpSmsSender


class SmsGatewayTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = Settings()

    async def test_gateway_contract_and_auth(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json={'success': True, 'request_id': 'test'})

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        with (
            patch.object(self.config, 'sms_gateway_url', 'https://sms.example.test/send'),
            patch.object(self.config, 'sms_gateway_token', SecretStr('test-gateway-token')),
            patch('app.services.sms.httpx.AsyncClient', return_value=client),
        ):
            await HttpSmsSender(self.config).send('+8613900000000', 'register', '123456')
        self.assertEqual(requests[0].headers['Authorization'], 'Bearer test-gateway-token')
        self.assertEqual(
            json.loads(requests[0].content),
            {'phone': '+8613900000000', 'scene': 'register', 'code': '123456', 'ttl_seconds': 300},
        )

    async def test_gateway_rejection_does_not_expose_provider_body(self):
        client = httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200, json={'success': False, 'debug': 'secret-code-123456'}
                )
            )
        )
        with (
            patch.object(self.config, 'sms_gateway_url', 'https://sms.example.test/send'),
            patch('app.services.sms.httpx.AsyncClient', return_value=client),
        ):
            with self.assertRaises(HTTPException) as raised:
                await HttpSmsSender(self.config).send('+8613900000000', 'login', '123456')
        self.assertEqual(raised.exception.status_code, 503)
        self.assertNotIn('123456', raised.exception.detail)

    async def test_missing_or_insecure_production_gateway_fails_closed(self):
        for url, token in [
            (None, None),
            ('http://sms.example.test', SecretStr('secret')),
            ('https://sms.example.test', None),
        ]:
            with (
                patch.object(self.config, 'environment', 'production'),
                patch.object(self.config, 'sms_gateway_url', url),
                patch.object(self.config, 'sms_gateway_token', token),
            ):
                with self.assertRaises(HTTPException) as raised:
                    HttpSmsSender(self.config)
                self.assertEqual(raised.exception.status_code, 503)
