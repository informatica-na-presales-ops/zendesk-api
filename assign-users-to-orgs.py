import csv
import logging
import notch
import os
import zendesk

notch.configure()
log = logging.getLogger(__name__)

z = zendesk.ZendeskClient(os.getenv('ZENDESK_COMPANY'), os.getenv('ZENDESK_USERNAME'), os.getenv('ZENDESK_PASSWORD'))

with open('zendesk-people.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = int(row.get('user_id'))
        user = z.get_user_by_id(user_id)

        new_orgs_str = row.get('new_organizations')
        if new_orgs_str:
            new_orgs_set = set(new_orgs_str.split('|'))
        else:
            log.info(f'Skipping {user.email}, no new organizations set')
            continue

        old_orgs_str = row.get('old_organizations')
        if old_orgs_str:
            old_orgs_set = set(old_orgs_str.split('|'))
        else:
            old_orgs_set = set()

        orgs_to_add = new_orgs_set - old_orgs_set
        orgs_to_del = old_orgs_set - new_orgs_set

        log.info(f'Processing org changes for {user.email}')

        for org_name in orgs_to_add:
            org = z.get_organization_by_name(org_name)
            log.info(f'** Adding {user.email} to {org_name}')
            user.add_org_membership(org)
        for org_name in orgs_to_del:
            org = z.get_organization_by_name(org_name)
            log.info(f'** Removing {user.email} from {org_name}')
            user.unassign_organization(org)
