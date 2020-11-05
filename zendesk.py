import logging
import requests
import requests.auth

from typing import Dict, List

log = logging.getLogger(__name__)


class ZendeskClient:
    def __init__(self, company: str, username: str, password: str):
        self.base_url = f'https://{company}.zendesk.com/api/v2'
        log.debug(f'Zendesk base url is {self.base_url}')
        self.s = requests.Session()
        self.s.auth = requests.auth.HTTPBasicAuth(username, password)
        self.s.headers.update({'accept': 'application/json'})

    def _get(self, url: str, params: dict = None):
        log.debug(f'Getting {url}')
        response = self.s.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _put(self, url: str, json: Dict):
        log.debug(f'Putting {url} / {json}')
        response = self.s.put(url, json=json)
        response.raise_for_status()
        return response.json()

    def get_ticket_field_options(self, field_id: int):
        _url = f'{self.base_url}/ticket_fields/{field_id}/options.json'
        while _url is not None:
            data = self._get(_url)
            _url = data.get('next_page')
            _options = data.get('custom_field_options', [])
            yield from [ZendeskCustomFieldOption(self, o) for o in _options]

    def list_user_identities(self, user_id: int):
        _url = f'{self.base_url}/users/{user_id}/identities.json'
        while _url is not None:
            data = self._get(_url)
            _url = data.get('next_page')
            _identities = data.get('identities')
            yield from [ZendeskUserIdentity(self, i) for i in _identities]

    def search_users(self, query: str):
        _url = f'{self.base_url}/users/search.json'
        params = {'query': query}
        data = self._get(_url, params)
        return data

    @property
    def ticket_fields(self):
        _url = f'{self.base_url}/ticket_fields.json'
        data = self._get(_url)
        _ticket_fields = data.get('ticket_fields', [])
        yield from [ZendeskTicketField(self, f) for f in _ticket_fields]

    @property
    def tickets(self):
        _url = f'{self.base_url}/tickets.json'
        while _url is not None:
            data = self._get(_url)
            _url = data.get('next_page')
            _tickets = data.get('tickets')
            yield from [ZendeskTicket(self, i) for i in _tickets]

    def update_ticket(self, ticket_id: int, params: Dict):
        _url = f'{self.base_url}/tickets/{ticket_id}.json'
        json = {'ticket': params}
        data = self._put(_url, json)
        return data

    def update_user(self, user_id: int, params: Dict):
        _url = f'{self.base_url}/users/{user_id}.json'
        json = {'user': params}
        data = self._put(_url, json)
        return data

    @property
    def users(self):
        _url = f'{self.base_url}/users.json'
        while _url is not None:
            data = self._get(_url)
            _url = data.get('next_page')
            _users = data.get('users')
            yield from [ZendeskUser(self, u) for u in _users]


class ZendeskApiObject(dict):
    def __init__(self, client: ZendeskClient, *args, **kwargs):
        self.client = client
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int:
        return self.get('id')


class ZendeskTicket(ZendeskApiObject):
    @property
    def external_id(self) -> str:
        return self.get('external_id')

    @external_id.setter
    def external_id(self, value: str):
        params = dict(external_id=value)
        self.update(params)
        self.client.update_ticket(self.id, params)


class ZendeskCustomField(ZendeskApiObject):
    pass


class ZendeskCustomFieldOption(ZendeskApiObject):
    @property
    def name(self) -> str:
        return self.get('name')

    @property
    def value(self) -> str:
        return self.get('value')


class ZendeskTicketField(ZendeskCustomField):
    @property
    def options(self) -> List[ZendeskCustomFieldOption]:
        return [ZendeskCustomFieldOption(self.client, o) for o in self.get('custom_field_options')]

    @property
    def title(self) -> str:
        return self.get('title')

    @property
    def type(self) -> str:
        return self.get('type')


class ZendeskUser(ZendeskApiObject):
    @property
    def email(self) -> str:
        return self.get('email')

    @property
    def emails(self) -> List[str]:
        return [i.value for i in self.identities if i.is_email]

    @property
    def external_id(self) -> str:
        return self.get('external_id')

    @external_id.setter
    def external_id(self, value):
        response = self.client.update_user(self.id, {'external_id': value})
        self.update(response.get('user'))

    @property
    def identities(self):
        yield from self.client.list_user_identities(self.id)

    @property
    def name(self) -> str:
        return self.get('name')

    @property
    def suspended(self) -> bool:
        return self.get('suspended')


class ZendeskUserIdentity(ZendeskApiObject):
    @property
    def is_email(self):
        return self.type == 'email'

    @property
    def type(self):
        return self.get('type')

    @property
    def value(self):
        return self.get('value')
