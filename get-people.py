import csv
import os
import sys
import zendesk


def main():
    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow(['user_id', 'name', 'email', 'organizations', 'role', 'restricted_agent', 'ticket_restriction'])
    company = os.getenv('ZENDESK_COMPANY')
    username = os.getenv('ZENDESK_USERNAME')
    password = os.getenv('ZENDESK_PASSWORD')
    z = zendesk.ZendeskClient(company, username, password)

    for user in z.users:
        org_names = '|'.join([o.name for o in user.organizations])
        csv_writer.writerow([
            user.id, user.name, user.email, org_names, user.role, user.restricted_agent, user.ticket_restriction
        ])


if __name__ == '__main__':
    main()
