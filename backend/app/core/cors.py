# app/utils/cors.py
from fastapi.middleware.cors import CORSMiddleware


class CORSSetup:
    def __init__(
        self,
        app,
        allow_origins: list[str] = ["*"],
        allow_credentials: bool = True,
        allow_methods: list[str] = ["*"],
        allow_headers: list[str] = ["*"],
    ):
        self.app = app
        self.allow_origins = allow_origins
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers

    def setup(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allow_origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
        )

