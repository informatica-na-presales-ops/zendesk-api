import notch
import os
import zendesk

notch.configure()

company = os.getenv('ZENDESK_COMPANY')
username = os.getenv('ZENDESK_USERNAME')
password = os.getenv('ZENDESK_PASSWORD')
z = zendesk.ZendeskClient(company, username, password)

for user in z.users:
    if user.role == 'agent' and user.restricted_agent:
        user.ticket_restriction = None
