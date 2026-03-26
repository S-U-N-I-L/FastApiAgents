from urllib.request import Request

from fastapi.exceptions import RequestValidationError
from starlette.responses import PlainTextResponse

from model.Customer import CustomerOut


def add_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
        print('got error here ', exc)
        return PlainTextResponse('error from handler', status_code=400)