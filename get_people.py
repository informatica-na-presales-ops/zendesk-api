import csv
import os
import requests
import sys


def main():
    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow(['Name', 'Email', 'Organization'])
    company = os.getenv('ZENDESK_COMPANY')
    users_url = f'https://{company}.zendesk.com/api/v2/users.json'
    orgs_url = f'https://{company}.zendesk.com/api/v2/organizations.json'
    email = os.getenv('ZENDESK_EMAIL')
    password = os.getenv('ZENDESK_PASSWORD')

    orgs = {None: 'None'}
    org_resp = requests.get(orgs_url, auth=(email, password))
    for org in org_resp.json()['organizations']:
        orgs[org['id']] = org['name']

    next_page_avail = True
    while next_page_avail:
        response = requests.get(users_url, auth=(email, password))
        data = response.json()
        next_page = data['next_page']
        if next_page is None:
            next_page_avail = False
        else:
            users_url = next_page
        users = data['users']
        for user in users:
            user_name = user['name']
            user_email = user['email']
            org_id = user['organization_id']
            org_name = orgs[org_id]
            csv_writer.writerow([user_name, user_email, org_name])


if __name__ == '__main__':
    main()
