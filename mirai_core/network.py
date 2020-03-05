from typing import Dict
import httpx
from .log import create_logger
from io import BytesIO

from .exceptions import AuthenticationException, NetworkException,\
    UnknownTargetException, PrivilegeException, BadRequestException, MiraiException


class HttpXClient:
    """HttpClient implemented by httpx."""

    DEFAULT_TIMEOUT = 30

    @staticmethod
    def _check_response(result: httpx.Response, url, method) -> Dict:
        if result.status_code != 200:
            raise NetworkException(f'{url} {method} failed')
        result = result.json()
        if method == 'post':
            status_code = result.get('code')
            if status_code is None:
                raise NetworkException('Empty response')
            if status_code == 0:  # normal
                return result
            elif status_code == 1:
                raise AuthenticationException('Incorrect authKey')
            elif status_code == 2:
                raise AuthenticationException('Bot does not exist')
            elif status_code == 3:
                raise AuthenticationException('Session expired')
            elif status_code == 4:
                raise AuthenticationException('Session is not verified')
            elif status_code == 5:
                raise UnknownTargetException('Message target does not exist')
            elif status_code == 10:
                raise PrivilegeException('Bot does not have corresponding privilege')
            elif status_code == 400:
                raise BadRequestException('Bad Request, please check arguments/url')
            else:
                raise MiraiException('HTTP API updated, please upgrade python-mirai-core')
        elif method == 'get':
            return result

    def __init__(self, base_url: str, timeout=DEFAULT_TIMEOUT):
        self.base_url = base_url
        self.session = httpx.AsyncClient(timeout=timeout)
        self.timeout = timeout
        self.logger = create_logger('Network')

    async def get(self, url, headers=None, params=None, timeout=None):
        if timeout is None:
            timeout = self.timeout
        if url != '/fetchMessage':
            self.logger.debug(f'get {url} with params: {str(params)}')

        response = await self.session.get(self.base_url + url, headers=headers, params=params, timeout=timeout)
        return HttpXClient._check_response(response, url, 'get')

    async def post(self, url, headers=None, data=None, timeout=None):
        if timeout is None:
            timeout = self.timeout

        self.logger.debug(f'post {url} with data: {str(data)}')

        response = await self.session.post(self.base_url + url, headers=headers, json=data, timeout=timeout)
        return HttpXClient._check_response(response, url, 'post')

    async def upload(self, url, headers=None, data=None, file: str = None, timeout=None):
        files = {
            'img': BytesIO(open(str(file.absolute()), 'rb').read())
        }
        self.logger.debug(f'upload {url} with file: {file}')
        response = await self.session.post(self.base_url + url, data=data,
                                           headers=headers, files=files, timeout=timeout)
        return response.text

    async def close(self):
        await self.session.aclose()
