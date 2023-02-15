import csv
import os
import sys
import zendesk


def main():
    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow([
        'user_id', 'name', 'employee_id', 'active', 'verified', 'last_login_at', 'email', 'organizations', 'role',
        'agent_groups', 'restricted_agent', 'ticket_restriction', 'suspended'
    ])
    company = os.getenv('ZENDESK_COMPANY')
    username = os.getenv('ZENDESK_USERNAME')
    password = os.getenv('ZENDESK_PASSWORD')
    z = zendesk.ZendeskClient(company, username, password)

    for user in z.users:
        org_names = '|'.join(sorted([o.name for o in user.organizations]))
        group_names = '|'.join(sorted([g.name for g in user.groups]))
        csv_writer.writerow([
            user.id, user.name, user.external_id, user.active, user.verified, user.last_login_at, user.email, org_names,
            user.role, group_names, user.restricted_agent, user.ticket_restriction, user.suspended
        ])


if __name__ == '__main__':
    main()
