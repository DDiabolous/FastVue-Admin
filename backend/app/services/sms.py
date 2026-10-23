"""短信联调不发消息；真实模式使用 HTTP 网关，不返回或打印验证码。"""

from urllib.parse import urlparse
import httpx
from fastapi import HTTPException, Request
from app.core.config import Settings


class HttpSmsSender:
    def __init__(self, config: Settings):
        url = config.sms_gateway_url or ''
        parsed = urlparse(url)
        if (
            parsed.scheme not in ('http', 'https')
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise HTTPException(503, '短信网关未配置')
        self.token = config.sms_gateway_token.get_secret_value() if config.sms_gateway_token else ''
        if config.environment == 'production' and (parsed.scheme != 'https' or not self.token):
            raise HTTPException(503, '生产短信网关需要 HTTPS 和鉴权配置')
        self.url = url

    async def send(self, phone, scene, code):
        try:
            async with httpx.AsyncClient(timeout=5, follow_redirects=False) as client:
                result = await client.post(
                    self.url,
                    json={
                        'phone': phone,
                        'scene': scene,
                        'code': code,
                        'ttl_seconds': 300,
                    },
                    headers={'Authorization': f'Bearer {self.token}'} if self.token else {},
                )
                result.raise_for_status()
                if result.json().get('success') is not True:
                    raise ValueError('gateway did not confirm delivery acceptance')
        except (httpx.HTTPError, ValueError, AttributeError):
            raise HTTPException(503, '短信发送失败，请稍后重试') from None


class MockSmsSender:
    """联调模式不调用网关；任意六位数字校验由 UserAuthStore 处理。"""

    async def send(self, phone, scene, code):
        return None


def get_sms_sender(request: Request):
    config = request.app.state.config
    if config.user_sms_mock_enabled:
        return MockSmsSender()
    return HttpSmsSender(config)
