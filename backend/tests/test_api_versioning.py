from app.main import create_app


async def test_unversioned_business_routes_and_unknown_versions_are_not_exposed(client):
    for path in [
        '/api/auth/login',
        '/api/users',
        '/api/settings/public',
        '/api/v2/users',
        '/api/v1/health',
    ]:
        method = 'POST' if path.endswith('/login') else 'GET'
        response = await client.request(method, path)
        assert response.status_code == 404
    assert (await client.get('/api/health')).status_code == 200
    assert (await client.get('/api/v1/settings/public')).status_code == 200


def test_openapi_describes_versioned_contracts_and_safe_user_output():
    document = create_app().openapi()
    assert all(path == '/api/health' or path.startswith('/api/v1/') for path in document['paths'])
    operations = [operation for path in document['paths'].values() for operation in path.values()]
    identifiers = [operation['operationId'] for operation in operations]
    assert len(identifiers) == len(set(identifiers))
    user_output = document['components']['schemas']['UserRead']['properties']
    assert {'id', 'username', 'role', 'permissions'} <= user_output.keys()
    assert not {'password', 'password_hash', 'builtin', 'token_hash'} & user_output.keys()
    request_schema = document['paths']['/api/v1/users']['post']['requestBody']['content'][
        'application/json'
    ]['schema']
    assert request_schema['$ref'].endswith('/UserCreate')
    assert '/api/v1/auth/login' in document['paths']
