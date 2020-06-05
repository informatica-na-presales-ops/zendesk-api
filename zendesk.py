import logging
import requests
import requests.auth

log = logging.getLogger(__name__)


class ZendeskClient:
    def __init__(self, company: str, username: str, password: str):
        self.base_url = f'https://{company}.zendesk.com/api/v2'
        log.debug(f'Zendesk base url is {self.base_url}')
        self.s = requests.Session()
        self.s.auth = requests.auth.HTTPBasicAuth(username, password)
        self.s.headers.update({'accept': 'application/json'})

    @property
    def users(self):
        _url = f'{self.base_url}/users.json'
        while _url is not None:
            response = self.s.get(_url)
            data = response.json()
            _url = data.get('next_page')
            _users = data.get('users')
            yield from _users
