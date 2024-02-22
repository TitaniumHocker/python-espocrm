from requests import Response

from .types import EspoMethods


class EspoException(Exception):
    """Base exception for client."""


class InvalidRequestMethodError(EspoException):
    def __init__(self, method: str):
        self.method = method
        super().__init__(
            f"Invalid request method {self.method}, allowed: {map(str, EspoMethods)}"
        )


class EspoError(EspoException):
    """API Error."""

    def __init__(self, response: Response):
        self.code = response.status_code
        self.reason = response.headers.get("X-Status-Reason", "Unknown")
        super().__init__(f"Request failed with status code {self.code}: {self.reason}")


class EmptyResponseError(EspoException):
    def __init__(self):
        super().__init__("Got empty response")
