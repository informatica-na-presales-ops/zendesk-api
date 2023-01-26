import notch
import os
import zendesk

log = notch.make_log('zendesk_api.list_org_memberships')

z = zendesk.ZendeskClient(os.getenv('ZENDESK_COMPANY'), os.getenv('ZENDESK_USERNAME'), os.getenv('ZENDESK_PASSWORD'))

users = {u.id: u for u in z.users}

for m in z.organization_memberships:
    u: zendesk.ZendeskUser = users.get(m.user_id)
    log.info(f'{u.email} is a member of {m.organization_name}')
