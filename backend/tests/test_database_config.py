import pytest
from pydantic import ValidationError

from app import cli
from app.core.config import Settings


def test_database_url_is_required_without_env_file(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.setenv('USER_JWT_SECRET', 'private-key-must-not-appear-in-errors')
    with pytest.raises(ValidationError) as raised:
        Settings(_env_file=None)
    assert any(
        error['loc'] == ('database_url',) and error['type'] == 'missing'
        for error in raised.value.errors()
    )
    assert 'private-key-must-not-appear-in-errors' not in str(raised.value)


@pytest.mark.parametrize('url', ['', 'sqlite:///test.db'])
def test_empty_or_unsupported_database_url_is_rejected(url):
    with pytest.raises(ValidationError, match='DATABASE_URL must use postgresql'):
        Settings(_env_file=None, database_url=url)


def test_database_url_can_come_from_env_file_or_environment(tmp_path, monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    env_file = tmp_path / '.env'
    file_url = 'postgresql+asyncpg://file:password@127.0.0.1/file_db'
    process_url = 'postgresql+asyncpg://process:password@127.0.0.1/process_db'
    env_file.write_text(f'DATABASE_URL={file_url}\n')
    assert Settings(_env_file=env_file).database_url == file_url
    monkeypatch.setenv('DATABASE_URL', process_url)
    assert Settings(_env_file=env_file).database_url == process_url


@pytest.mark.parametrize('command', ['dev', 'serve'])
def test_missing_database_url_stops_server_before_uvicorn(monkeypatch, capsys, command):
    import uvicorn

    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.setattr(cli, 'get_settings', lambda: Settings(_env_file=None))
    monkeypatch.setattr('sys.argv', ['manage.py', command])

    def unexpected_start(*args, **kwargs):
        pytest.fail('Server must not start without DATABASE_URL')

    monkeypatch.setattr(uvicorn, 'run', unexpected_start)
    with pytest.raises(SystemExit) as raised:
        cli.main()
    assert raised.value.code == 1
    assert '缺少 DATABASE_URL' in capsys.readouterr().err
