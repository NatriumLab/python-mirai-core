from typing import Dict
import aiohttp
from aiohttp import client_exceptions
from .log import create_logger
from io import BytesIO

from .exceptions import AuthenticationException, NetworkException, ServerException, \
    UnknownTargetException, PrivilegeException, BadRequestException, MiraiException, SessionException


error_code = {
                1: AuthenticationException('Incorrect authKey'),
                2: AuthenticationException('Bot does not exist'),
                3: SessionException('Session does not exist or has expired'),
                4: AuthenticationException('Session is not verified'),
                5: UnknownTargetException('Message target does not exist'),
                10: PrivilegeException('Bot does not have corresponding privilege'),
                400: BadRequestException('Bad Request, please check arguments/url'),
            }


class HttpClient:
    """HttpClient implemented by aiohttp."""

    DEFAULT_TIMEOUT = 5

    @staticmethod
    async def _check_response(result: aiohttp.ClientResponse, url, method) -> Dict:
        if result.status != 200:
            raise ServerException(f'{url} {method} failed, status code: {result.status}')
        result = await result.json()
        status_code = result.get('code')
        if method == 'post':
            if status_code is None:
                raise ServerException('Empty response')
            if status_code == 0:  # normal
                return result
        elif method == 'get':
            if status_code is None or status_code == 0:
                return result
        if status_code in error_code:
            raise error_code[status_code]
        else:
            raise MiraiException('HTTP API updated, please upgrade python-mirai-core')

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT, loop=None):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(timeout)
        self.session = aiohttp.ClientSession(timeout=self.timeout, loop=loop)
        self.logger = create_logger('Network')
        self.loop = loop

    async def get(self, url, headers=None, params=None):
        if url != '/fetchMessage':
            self.logger.debug(f'get {url} with params: {str(params)}')
        try:
            response = await self.session.get(self.base_url + url, headers=headers, params=params)
        except client_exceptions.ClientConnectorError:
            raise NetworkException('Unable to reach Mirai console')
        return await HttpClient._check_response(response, url, 'get')

    async def post(self, url, headers=None, data=None):

        self.logger.debug(f'post {url} with data: {str(data)}')
        try:
            response = await self.session.post(self.base_url + url, headers=headers, json=data)
        except client_exceptions.ClientConnectorError:
            raise NetworkException('Unable to reach Mirai console')
        return await HttpClient._check_response(response, url, 'post')

    async def upload(self, url, headers=None, data=None, file: str = None):
        if data is None:
            data = dict()
        data['img'] = BytesIO(open(str(file.absolute()), 'rb').read())
        self.logger.debug(f'upload {url} with file: {file}')
        try:
            response = await self.session.post(self.base_url + url,
                                               headers=headers, data=data)
        except client_exceptions.ClientConnectorError:
            raise NetworkException('Unable to reach Mirai console')
        self.logger.debug(f'Image uploaded: {response.text}')
        return await response.json()

    async def websocket(self, url: str, handler: callable, ws_close_handler: callable):
        try:
            ws = await self.session.ws_connect(self.base_url + url)
            self.logger.debug('Websocket established')
            while True:
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self.logger.debug(f'Websocket received {msg}')
                    await handler(msg.json())
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    self.logger.debug('Websocket closed')
                    await ws_close_handler()
                    return
                else:
                    self.logger.warning(f'Received unexpected type: {msg.type}')
        except client_exceptions.ClientConnectorError:
            raise NetworkException('Unable to reach Mirai console')

    async def close(self):
        await self.session.close()
