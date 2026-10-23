import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.mark.parametrize('environment', ['production', ' Production '])
def test_production_rejects_mock_sms(monkeypatch, environment):
    monkeypatch.setenv('ENVIRONMENT', environment)
    monkeypatch.setenv('USER_SMS_MOCK_ENABLED', 'true')
    with pytest.raises(ValidationError, match='must be false in production'):
        Settings(_env_file=None)


def test_production_defaults_to_real_sms(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.delenv('USER_SMS_MOCK_ENABLED', raising=False)
    assert Settings(_env_file=None).user_sms_mock_enabled is False


def test_development_allows_explicit_mock_sms(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT', 'development')
    monkeypatch.setenv('USER_SMS_MOCK_ENABLED', 'true')
    assert Settings(_env_file=None).user_sms_mock_enabled is True
