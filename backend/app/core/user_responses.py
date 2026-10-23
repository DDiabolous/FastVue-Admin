from fastapi import Response


def result(data=None, message='success'):
    return {'code': 200, 'message': message, 'data': data}


def no_store(res: Response):
    res.headers['Cache-Control'] = 'no-store'
    res.headers['Pragma'] = 'no-cache'
