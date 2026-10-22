import logging

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException


class AppError(Exception):
    """Business error independent of the HTTP framework."""

    def __init__(self, code, message, headers=None):
        super().__init__(message)
        self.code, self.message, self.headers = code, message, headers


def error_response(code, message, headers=None):
    return JSONResponse(
        {'code': code, 'message': message, 'data': None}, status_code=code, headers=headers
    )


def register_exception_handlers(app):
    @app.exception_handler(AppError)
    async def business_error(request, exc):
        return error_response(exc.code, exc.message, exc.headers)

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error_response(exc.status_code, str(exc.detail), exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        fields = ', '.join('.'.join(str(part) for part in error['loc']) for error in exc.errors())
        return error_response(422, f'参数不正确：{fields}')

    @app.exception_handler(IntegrityError)
    async def conflict(request, exc):
        return error_response(409, '标识已存在或记录仍被引用')

    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        logging.getLogger('fastvue').error('Request failed (%s)', type(exc).__name__)
        return error_response(500, '服务暂时不可用，请稍后重试')
