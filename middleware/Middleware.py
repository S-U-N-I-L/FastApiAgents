from urllib.request import Request

from fastapi import FastAPI


def middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_middleware(request: Request, call_next):
        print('middle ware intercepting')
        response = await call_next(request)
        print('middleware intercepted')
        return response