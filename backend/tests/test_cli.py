from argparse import Namespace
from unittest.mock import Mock

import pytest

from app import cli


@pytest.mark.parametrize('command,reload', [('dev', True), ('serve', False)])
def test_server_commands_only_start_the_server(monkeypatch, command, reload):
    import uvicorn

    run = Mock()
    migrate = Mock()
    monkeypatch.setattr(uvicorn, 'run', run)
    monkeypatch.setattr(cli, 'migrate_database', migrate)
    monkeypatch.setattr('sys.argv', ['manage.py', command, '--port', '8015'])
    cli.main()
    migrate.assert_not_called()
    assert run.call_args.kwargs['reload'] is reload
    assert run.call_args.kwargs['port'] == 8015
    assert run.call_args.kwargs['host'] == '127.0.0.1'
    assert run.call_args.kwargs['proxy_headers'] is False


async def test_repeat_initialization_skips_password_prompt(app, monkeypatch):
    monkeypatch.setattr(cli, 'create_database', lambda _: (app.state.engine, app.state.sessions))
    prompt = Mock(side_effect=AssertionError('Existing databases must not prompt for a password'))
    monkeypatch.setattr(cli.getpass, 'getpass', prompt)
    monkeypatch.delenv('ADMIN_PASSWORD', raising=False)
    await cli.run(Namespace(command='setup', demo=False))
    prompt.assert_not_called()
