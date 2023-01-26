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

    def _get(self, url: str, params: dict = None):
        log.debug(f'Getting {url}')
        response = self.s.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _put(self, url: str, json: dict):
        log.debug(f'Putting {url} / {json}')
        response = self.s.put(url, json=json)
        response.raise_for_status()
        return response.json()

    def get_incremental_tickets(self, start_time: int):
        _url = f'{self.base_url}/incremental/tickets/cursor.json'
        params = {
            'start_time': start_time
        }
        data = self._get(_url, params)
        yield from [ZendeskTicket(self, t) for t in data.get('tickets', [])]

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

    @property
    def organizations(self):
        _url = f'{self.base_url}/organizations.json'
        while _url is not None:
            data = self._get(_url)
            _url = data.get('next_page')
            _orgs = data.get('organizations')
            yield from [ZendeskOrganization(self, i) for i in _orgs]

    def search(self, query: str, sort_by: str = None, sort_order: str = 'desc'):
        _url = f'{self.base_url}/search.json'
        params = {
            'query': query,
            'sort_order': sort_order
        }
        if sort_by is not None:
            params.update({
                'sort_by': sort_by
            })
        data = self._get(_url, params)
        return data

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

    def update_organization(self, org_id: int, params: dict):
        _url = f'{self.base_url}/organizations/{org_id}.json'
        json = {'organization': params}
        data = self._put(_url, json)
        return data

    def update_ticket(self, ticket_id: int, params: dict):
        _url = f'{self.base_url}/tickets/{ticket_id}.json'
        json = {'ticket': params}
        data = self._put(_url, json)
        return data

    def update_user(self, user_id: int, params: dict):
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

    @property
    def url(self) -> str:
        return self.get('url')


class ZendeskCustomField(ZendeskApiObject):
    pass


class ZendeskCustomFieldOption(ZendeskApiObject):
    @property
    def name(self) -> str:
        return self.get('name')

    @property
    def value(self) -> str:
        return self.get('value')


class ZendeskOrganization(ZendeskApiObject):
    @property
    def name(self) -> str:
        return self.get('name')

    @name.setter
    def name(self, value: str):
        params = dict(name=value)
        self.update(params)
        self.client.update_organization(self.id, params)


class ZendeskTicket(ZendeskApiObject):
    @property
    def external_id(self) -> str:
        return self.get('external_id')

    @external_id.setter
    def external_id(self, value: str):
        params = dict(external_id=value)
        self.update(params)
        self.client.update_ticket(self.id, params)

    def remove_email_cc(self, email: str):
        params = {
            'email_ccs': [
                {
                    'action': 'delete',
                    'user_email': email,
                }
            ]
        }
        return self.client.update_ticket(self.id, params)


class ZendeskTicketField(ZendeskCustomField):
    @property
    def options(self) -> list[ZendeskCustomFieldOption]:
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
    def emails(self) -> list[str]:
        return [i.value for i in self.identities if i.is_email]

    @property
    def external_id(self) -> str:
        return self.get('external_id')

    @external_id.setter
    def external_id(self, value: str):
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
