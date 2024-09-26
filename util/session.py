import random

from requests import Response
from browserforge.fingerprints import FingerprintGenerator
from curl_cffi.requests import Session as RequestsSession

from settings import settings
from logger.logger import Logger
from util.decorators import retry

logger = Logger("Session")


class Session(RequestsSession):
    def __init__(self, proxy: list[str] = settings["PROXIES"]) -> None:
        super(Session, self).__init__()
        self.headers.update(self.generate_fingerprint())

        self.get('https://www.google.com/')  # we add some cookies so the session is not empty
        if isinstance(proxy, list):
            if isinstance(proxy, list): proxy = random.choice(proxy)
            self.proxies = {"https": proxy, "http": proxy}  # then we add the proxies after so we check proxies
            logger.info(f'proxy: {proxy} is implemented.')

        logger.debug('Session initialized successfully')

    def generate_fingerprint(self, user_agent: str = None) -> dict:
        fingerprint = FingerprintGenerator()
        headers = fingerprint.generate(user_agent=user_agent or self.headers.get('User-Agent')).headers
        return headers

    @retry
    def get(self, *args, **kwargs) -> Response:
        """ GET request with retry decorator """
        response = super(Session, self).get(timeout=120, impersonate="chrome99", verify=False, *args, **kwargs)
        if not response:
            logger.error('GET request failed')
            return Response()
        return response

    @retry
    def post(self, *args, **kwargs) -> Response:
        """ POST request with retry decorator """
        response = super(Session, self).post(timeout=120, impersonate="chrome99", verify=False, *args, **kwargs)
        if not response:
            logger.error('POST request failed')
            return Response()
        return response
