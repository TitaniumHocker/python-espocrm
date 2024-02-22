import typing as t
from os import path
from urllib.parse import urlencode, urljoin

from requests import Session

from .exceptions import (EmptyResponseError, EspoError,
                         InvalidRequestMethodError)
from .types import EspoMethods


def _http_build_query(data):
    """Query builder taken from EspoCRM documentation.

    :see: https://docs.espocrm.com/development/api-client-python/
    """
    parents = list()
    pairs = dict()

    def renderKey(parents):
        depth, outStr = 0, ""
        for x in parents:
            s = "[%s]" if depth > 0 or isinstance(x, int) else "%s"
            outStr += s % str(x)
            depth += 1
        return outStr

    def r_urlencode(data):
        if isinstance(data, list) or isinstance(data, tuple):
            for i in range(len(data)):
                parents.append(i)
                r_urlencode(data[i])
                parents.pop()
        elif isinstance(data, dict):
            for key, value in data.items():
                parents.append(key)
                r_urlencode(value)
                parents.pop()
        else:
            pairs[renderKey(parents)] = str(data)

        return pairs

    return urlencode(r_urlencode(data))


class Espo:
    def __init__(self, url: str, token: str, prefix: str = "/api/v1/"):
        self.base = url
        self.prefix = prefix
        self.token = token
        self.session = Session()
        self.session.headers["X-Api-Key"] = token

    def make_url(self, action: str) -> str:
        return urljoin(urljoin(self.base, self.prefix), action)

    def request(
        self,
        method: EspoMethods,
        action: str,
        params: dict[str, t.Any] | None = None,
    ):
        if params is None:
            params = {}

        kwargs: dict[str, t.Any] = {
            "url": self.make_url(action),
        }


        match method:
            case EspoMethods.POST | EspoMethods.PATCH | EspoMethods.PUT:
                kwargs["json"] = params
            case EspoMethods.GET | EspoMethods.DELETE:
                kwargs["url"] = f"{self.make_url(action)}?{_http_build_query(params)}"
            case _:
                raise InvalidRequestMethodError(method)

        response = self.session.request(method, **kwargs)

        if response.status_code != 200:
            raise EspoError(response)

        if not response.content:
            raise EmptyResponseError

        return response.json()
