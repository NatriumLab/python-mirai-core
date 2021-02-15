from typing import Dict
import aiohttp
from aiohttp import client_exceptions
from .log import create_logger
from io import BytesIO

from .exceptions import AuthenticationException, NetworkException, ServerException, \
    UnknownTargetException, PrivilegeException, BadRequestException, MiraiException, SessionException


error_code = {
                1: lambda: AuthenticationException('Incorrect authKey'),
                2: lambda: AuthenticationException('Bot does not exist, please login in console'),
                3: lambda: SessionException('Session does not exist or has expired'),
                4: lambda: AuthenticationException('Session is not verified'),
                5: lambda: UnknownTargetException('Message target does not exist'),
                6: lambda: UnknownTargetException('File target does not exist'),
                10: lambda: PrivilegeException('Bot does not have corresponding privilege'),
                20: lambda: PrivilegeException('Bot is banned in group'),
                30: lambda: PrivilegeException('Message is too long'),
                400: lambda: BadRequestException('Bad Request, please check arguments/url'),
            }


class HttpClient:
    """
    Internal use only
    HttpClient implemented by aiohttp
    """

    DEFAULT_TIMEOUT = 5

    @staticmethod
    async def _check_response(result: aiohttp.ClientResponse, url, method) -> Dict:
        """
        Check url response, and raise exceptions

        :param result: http response
        :param url: url to show in the log
        :param method: 'post', 'get'
        :return: json decoded result
        """
        if result.status != 200:
            raise ServerException(f'{url} {method} failed, status code: {result.status}')
        result = await result.json()
        if not isinstance(result, dict):
            return result
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
            raise error_code[status_code]()
        else:
            raise MiraiException('HTTP API updated, please upgrade python-mirai-core')

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT, loop=None):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(timeout)
        self.session = aiohttp.ClientSession(timeout=self.timeout, loop=loop)
        self.logger = create_logger('Network')
        self.loop = loop

    async def get(self, url, headers=None, params=None):
        """
        send http get request

        :param url: the sub url
        :param headers: request headers
        :param params: get params
        :return: json decoded response
        """
        if url != '/fetchMessage':
            self.logger.debug(f'get {url} with params: {str(params)}')
        try:
            response = await self.session.get(self.base_url + url, headers=headers, params=params)
        except client_exceptions.ClientConnectorError:
            raise NetworkException('Unable to reach Mirai console')
        return await HttpClient._check_response(response, url, 'get')

    async def post(self, url, headers=None, data=None):
        """
        send http post request

        :param url: the sub url
        :param headers: request headers
        :param data: post params
        :return: json decoded response
        """

        self.logger.debug(f'post {url} with data: {str(data)}')
        try:
            response = await self.session.post(self.base_url + url, headers=headers, json=data)
        except client_exceptions.ClientConnectorError:
            raise NetworkException('Unable to reach Mirai console')
        return await HttpClient._check_response(response, url, 'post')

    async def upload(self, url, headers=None, data=None, file: str = None):
        """
        upload using multipart upload

        :param url: the sub url
        :param headers: request headers
        :param data: post params
        :param file: file to attach
        :return: json decoded response
        """
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
        """
        Create websocket subscriber to url

        :param url: the sub url
        :param handler: request headers
        :param ws_close_handler: callback for connection close
        """
        try:
            ws = await self.session.ws_connect(self.base_url + url, heartbeat=HttpClient.DEFAULT_TIMEOUT)
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
        """
        Close session
        """
        await self.session.close()
