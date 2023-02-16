import attrs
import logging

from aiohttp import ClientSession, ClientResponse
from aiohttp.client_exceptions import ClientError

from inspect import iscoroutinefunction

from typing import Literal, Any

from .schemas import Request


@attrs.define
class BaseMiddleware:
    
    def pre_request(self, *args, **kwargs) -> Any:
        """ Method allows to process request before requesting. """
        raise NotImplementedError

    def post_response(self, *args, **kwargs) -> Any:
        """ Method allows to process response after responding. """
        raise NotImplementedError


@attrs.define
class ClientMiddleware(BaseMiddleware):
    allow_methods: list = attrs.field(default=['GET'])

    @staticmethod
    def is_valid_response(response: ClientResponse) -> bool:
        """ Method allows validate response by status code """
        return 200 <= response.status < 300

    def pre_request(self, request: Request) -> None:
        if request.method.upper() not in self.allow_methods:
            raise ClientError(f'Method: {request.method} not in allow methods.')

    async def post_response(self, response: ClientResponse) -> Any:
        if not self.is_valid_response(response):
            message = await response.text(encoding='utf-8')
            err_text = f'Bad response: {response.status} | {message}'
            logging.error(err_text)
            raise ClientError(err_text)


@attrs.define
class BaseClient:

    base_url: str = attrs.field(default='https://api.nasa.gov', kw_only=True)
    _session: ClientSession = attrs.field(
        validator=attrs.validators.instance_of(ClientSession), 
        kw_only=True,
        alias='session'
    )
    _middleware: ClientMiddleware | BaseMiddleware = attrs.field(
        validator=attrs.validators.instance_of(BaseMiddleware),
        default=ClientMiddleware(), kw_only=True
    )

    @property
    def session(self) -> ClientSession:
        return self._session

    async def middleware(
        self,
        stage: Literal['PRE', 'POST'], 
        RequestOrResponse: Request | ClientResponse
    ) -> Any:
        """ 
        Method encapsulates middleware handlers and calls them depending on:
        stage: name of stage
        sync/async: method type
        """
        match stage.upper():
            case 'PRE':
                handler = self._middleware.pre_request
            case 'POST':
                handler = self._middleware.post_response
        if iscoroutinefunction(handler):
            return await handler(RequestOrResponse)
        return handler(RequestOrResponse)

    async def request(self, request: Request) -> ClientResponse:
        """
        The method implements a basic request to the server and embeds middleware handling.
        """
        if not request.force:
            await self.middleware('PRE', request)

        response = await self._session.request(request.method, request.url, **request.kwargs)

        if request.force:
            return response

        await self.middleware('POST', response)
        return response

    async def get(
        self, 
        endpoint: str,
        json_resp: bool = False,
        **kwargs
    ) -> str:
        """ GET method. """
        method = 'GET'
        url = self.base_url + endpoint
        request_data = Request(method=method, url=url, kwargs=kwargs)
        resp = await self.request(request_data)

        if json_resp:
            data = await resp.json()
            resp.close()
            return data

        data = await resp.text()
        resp.close()
        return data
