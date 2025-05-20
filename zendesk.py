import datetime
import logging
import requests
import requests.auth

from typing import Optional

log = logging.getLogger(__name__)


class ZendeskClient:
    _group_memberships = None
    _groups = None
    _organization_memberships = None
    _organizations = None
    _users = None

    def __init__(self, company: str, username: str, password: str):
        self.base_url = f"https://{company}.zendesk.com/api/v2"
        log.debug(f"Zendesk base url is {self.base_url}")
        self.s = requests.Session()
        self.s.auth = requests.auth.HTTPBasicAuth(username, password)
        self.s.headers.update({"accept": "application/json"})

    def _delete(self, url: str):
        log.debug(f"DELETE {url}")
        response = self.s.delete(url)
        response.raise_for_status()
        # return response.json()

    def _get(self, url: str, params: dict = None):
        log.debug(f"GET {url}")
        response = self.s.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, url: str, json: dict):
        log.debug(f"POST {url} / {json}")
        response = self.s.post(url, json=json)
        response.raise_for_status()
        return response.json()

    def _put(self, url: str, json: dict):
        log.debug(f"PUT {url} / {json}")
        response = self.s.put(url, json=json)
        response.raise_for_status()
        return response.json()

    def create_organization_membership(self, user_id: int, organization_id: int):
        url = f"{self.base_url}/organization_memberships.json"
        json = {
            "organization_membership": {
                "organization_id": organization_id,
                "user_id": user_id,
            },
        }
        return self._post(url, json)

    def get_group_by_id(self, group_id: int) -> Optional["ZendeskGroup"]:
        for group in self.groups:
            if group.id == group_id:
                return group
        return None

    def get_group_by_name(self, group_name: str) -> Optional["ZendeskGroup"]:
        for group in self.groups:
            if group.name == group_name:
                return group
        return None

    def get_incremental_tickets(self, start_time: int):
        _url = f"{self.base_url}/incremental/tickets/cursor.json"
        params = {"start_time": start_time}
        data = self._get(_url, params)
        yield from [ZendeskTicket(self, t) for t in data.get("tickets", [])]

    def get_organization_by_id(
        self, organization_id: int
    ) -> Optional["ZendeskOrganization"]:
        for org in self.organizations:
            if org.id == organization_id:
                return org
        return None

    def get_organization_by_name(
        self, organization_name: str
    ) -> Optional["ZendeskOrganization"]:
        for org in self.organizations:
            if org.name == organization_name:
                return org
        return None

    def get_ticket_field_options(self, field_id: int):
        _url = f"{self.base_url}/ticket_fields/{field_id}/options.json"
        while _url is not None:
            data = self._get(_url)
            _url = data.get("next_page")
            _options = data.get("custom_field_options", [])
            yield from [ZendeskCustomFieldOption(self, o) for o in _options]

    def get_user_by_id(self, user_id: int) -> Optional["ZendeskUser"]:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    @property
    def group_memberships(self) -> list["ZendeskGroupMembership"]:
        if self._group_memberships is None:
            result = []
            url = f"{self.base_url}/group_memberships.json"
            params = {
                "page[size]": 100,
            }
            has_more = True
            while has_more:
                data = self._get(url, params)
                _memberships = data.get("group_memberships")
                result.extend([ZendeskGroupMembership(self, i) for i in _memberships])
                has_more = data.get("meta").get("has_more")
                params.update(
                    {
                        "page[after]": data.get("meta").get("after_cursor"),
                    }
                )
            self._group_memberships = result
        return self._group_memberships

    @property
    def groups(self) -> list["ZendeskGroup"]:
        if self._groups is None:
            result = []
            url = f"{self.base_url}/groups.json"
            params = {
                "page[size]": 100,
            }
            has_more = True
            while has_more:
                data = self._get(url, params)
                _groups = data.get("groups")
                result.extend([ZendeskGroup(self, i) for i in _groups])
                has_more = data.get("meta").get("has_more")
                params.update(
                    {
                        "page[after]": data.get("meta").get("after_cursor"),
                    }
                )
            self._groups = result
        return self._groups

    def list_group_memberships_for_user(self, user_id: int):
        for m in self.group_memberships:
            if m.user_id == user_id:
                yield m

    def list_memberships_for_group(self, group_id: int):
        for m in self.group_memberships:
            if m.group_id == group_id:
                yield m

    def list_memberships_for_org(self, organization_id: int):
        for m in self.organization_memberships:
            if m.organization_id == organization_id:
                yield m

    def list_org_memberships_for_user(self, user_id: int):
        for m in self.organization_memberships:
            if m.user_id == user_id:
                yield m

    def list_user_identities(self, user_id: int):
        _url = f"{self.base_url}/users/{user_id}/identities.json"
        while _url is not None:
            data = self._get(_url)
            _url = data.get("next_page")
            _identities = data.get("identities")
            yield from [ZendeskUserIdentity(self, i) for i in _identities]

    @property
    def organization_memberships(self):
        if self._organization_memberships is None:
            result = []
            url = f"{self.base_url}/organization_memberships.json"
            params = {
                "page[size]": 100,
            }
            has_more = True
            while has_more:
                data = self._get(url, params)
                _memberships = data.get("organization_memberships")
                result.extend(
                    [ZendeskOrganizationMembership(self, i) for i in _memberships]
                )
                has_more = data.get("meta").get("has_more")
                params.update(
                    {
                        "page[after]": data.get("meta").get("after_cursor"),
                    }
                )
            self._organization_memberships = result
        return self._organization_memberships

    @property
    def organizations(self):
        if self._organizations is None:
            log.debug("Fetching organization list for this client")
            result = []
            url = f"{self.base_url}/organizations.json"
            params = {
                "page[size]": 100,
            }
            has_more = True
            while has_more:
                data = self._get(url, params)
                orgs = data.get("organizations")
                result.extend([ZendeskOrganization(self, o) for o in orgs])
                has_more = data.get("meta").get("has_more")
                params.update(
                    {
                        "page[after]": data.get("meta").get("after_cursor"),
                    }
                )
            self._organizations = result
        return self._organizations

    def search(self, query: str, sort_by: str = None, sort_order: str = "desc"):
        _url = f"{self.base_url}/search.json"
        params = {"query": query, "sort_order": sort_order}
        if sort_by is not None:
            params.update({"sort_by": sort_by})
        data = self._get(_url, params)
        return data

    def search_users(self, query: str):
        _url = f"{self.base_url}/users/search.json"
        params = {"query": query}
        data = self._get(_url, params)
        return data

    @property
    def ticket_fields(self):
        _url = f"{self.base_url}/ticket_fields.json"
        data = self._get(_url)
        _ticket_fields = data.get("ticket_fields", [])
        yield from [ZendeskTicketField(self, f) for f in _ticket_fields]

    @property
    def tickets(self):
        _url = f"{self.base_url}/tickets.json"
        while _url is not None:
            data = self._get(_url)
            _url = data.get("next_page")
            _tickets = data.get("tickets")
            yield from [ZendeskTicket(self, i) for i in _tickets]

    def unassign_organization(self, user_id: int, organization_id: int):
        url = f"{self.base_url}/users/{user_id}/organizations/{organization_id}.json"
        return self._delete(url)

    def update_organization(self, org_id: int, params: dict):
        _url = f"{self.base_url}/organizations/{org_id}.json"
        json = {"organization": params}
        data = self._put(_url, json)
        return data

    def update_ticket(self, ticket_id: int, params: dict):
        _url = f"{self.base_url}/tickets/{ticket_id}.json"
        json = {"ticket": params}
        data = self._put(_url, json)
        return data

    def update_user(self, user_id: int, params: dict):
        _url = f"{self.base_url}/users/{user_id}.json"
        json = {"user": params}
        data = self._put(_url, json)
        return data

    @property
    def users(self) -> list["ZendeskUser"]:
        if self._users is None:
            result = []
            url = f"{self.base_url}/users.json"
            params = {
                "page[size]": 100,
            }
            has_more = True
            while has_more:
                data = self._get(url, params)
                _users = data.get("users")
                result.extend([ZendeskUser(self, u) for u in _users])
                has_more = data.get("meta").get("has_more")
                params.update(
                    {
                        "page[after]": data.get("meta").get("after_cursor"),
                    }
                )
            self._users = result
        return self._users


class ZendeskApiObject(dict):
    def __init__(self, client: ZendeskClient, *args, **kwargs):
        self.client = client
        super().__init__(*args, **kwargs)

    @property
    def id(self) -> int:
        return self.get("id")

    @property
    def url(self) -> str:
        return self.get("url")


class ZendeskCustomField(ZendeskApiObject):
    pass


class ZendeskCustomFieldOption(ZendeskApiObject):
    @property
    def name(self) -> str:
        return self.get("name")

    @property
    def value(self) -> str:
        return self.get("value")


class ZendeskGroup(ZendeskApiObject):
    @property
    def default(self):
        return self.get("default")

    @property
    def deleted(self):
        return self.get("deleted")

    @property
    def description(self):
        return self.get("description")

    @property
    def is_public(self):
        return self.get("is_public")

    @property
    def name(self):
        return self.get("name")


class ZendeskGroupMembership(ZendeskApiObject):
    @property
    def group_id(self):
        return self.get("group_id")

    @property
    def user_id(self):
        return self.get("user_id")


class ZendeskOrganization(ZendeskApiObject):
    _memberships = None

    def __str__(self):
        return self.name

    @property
    def memberships(self) -> list["ZendeskOrganizationMembership"]:
        if self._memberships is None:
            self._memberships = list(self.client.list_memberships_for_org(self.id))
        return self._memberships

    @property
    def name(self) -> str:
        return self.get("name")

    @name.setter
    def name(self, value: str):
        params = dict(name=value)
        self.update(params)
        self.client.update_organization(self.id, params)

    @property
    def tags(self) -> list[str]:
        return self.get("tags", [])

    @property
    def users(self) -> list["ZendeskUser"]:
        return [self.client.get_user_by_id(m.user_id) for m in self.memberships]


class ZendeskOrganizationMembership(ZendeskApiObject):
    @property
    def default(self) -> bool:
        return bool(self.get("default"))

    @property
    def organization_id(self) -> int:
        return self.get("organization_id")

    @property
    def organization_name(self) -> str:
        return self.get("organization_name")

    @property
    def user_id(self) -> int:
        return self.get("user_id")


class ZendeskTicket(ZendeskApiObject):
    @property
    def external_id(self) -> str:
        return self.get("external_id")

    @external_id.setter
    def external_id(self, value: str):
        params = dict(external_id=value)
        self.update(params)
        self.client.update_ticket(self.id, params)

    def remove_email_cc(self, email: str):
        params = {
            "email_ccs": [
                {
                    "action": "delete",
                    "user_email": email,
                }
            ]
        }
        return self.client.update_ticket(self.id, params)


class ZendeskTicketField(ZendeskCustomField):
    @property
    def options(self) -> list[ZendeskCustomFieldOption]:
        return [
            ZendeskCustomFieldOption(self.client, o)
            for o in self.get("custom_field_options")
        ]

    @property
    def title(self) -> str:
        return self.get("title")

    @property
    def type(self) -> str:
        return self.get("type")


class ZendeskUser(ZendeskApiObject):
    _groups = None
    _organizations = None

    def __str__(self):
        return self.name

    @property
    def active(self):
        return self.get("active")

    def add_org_membership(self, org: ZendeskOrganization):
        self.client.create_organization_membership(self.id, org.id)

    @property
    def email(self) -> str:
        return self.get("email")

    @property
    def emails(self) -> list[str]:
        return [i.value for i in self.identities if i.is_email]

    @property
    def external_id(self) -> str:
        return self.get("external_id")

    @external_id.setter
    def external_id(self, value: str):
        response = self.client.update_user(self.id, {"external_id": value})
        self.update(response.get("user"))

    @property
    def identities(self):
        yield from self.client.list_user_identities(self.id)

    @property
    def last_login_at(self):
        _str = self.get("last_login_at")
        if _str is None:
            return None
        return datetime.datetime.strptime(_str, "%Y-%m-%dT%H:%M:%S%z")

    @property
    def name(self) -> str:
        return self.get("name")

    @property
    def organization_id(self) -> int:
        return self.get("organization_id")

    @property
    def groups(self) -> list[ZendeskGroup]:
        if self._groups is None:
            result = []
            for m in self.client.list_group_memberships_for_user(self.id):
                result.append(self.client.get_group_by_id(m.group_id))
            self._groups = result
        return self._groups

    @property
    def organizations(self) -> list[ZendeskOrganization]:
        if self._organizations is None:
            result = []
            for m in self.client.list_org_memberships_for_user(self.id):
                result.append(self.client.get_organization_by_id(m.organization_id))
            self._organizations = result
        return self._organizations

    @property
    def restricted_agent(self) -> bool:
        return self.get("restricted_agent")

    @property
    def role(self) -> str:
        return self.get("role")

    @property
    def shared(self):
        return self.get("shared")

    @property
    def suspended(self) -> bool:
        return self.get("suspended")

    @property
    def ticket_restriction(self) -> str:
        return self.get("ticket_restriction")

    @ticket_restriction.setter
    def ticket_restriction(self, value: str):
        if value in ("assigned", "groups", "organization", "requested", None):
            response = self.client.update_user(self.id, {"ticket_restriction": value})
            self.update(response.get("user"))

    def unassign_organization(self, org: ZendeskOrganization):
        self.client.unassign_organization(self.id, org.id)

    @property
    def verified(self):
        return self.get("verified")


class ZendeskUserIdentity(ZendeskApiObject):
    @property
    def is_email(self):
        return self.type == "email"

    @property
    def type(self):
        return self.get("type")

    @property
    def value(self):
        return self.get("value")
