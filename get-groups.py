import csv
import os
import sys
import zendesk

csv_writer = csv.writer(sys.stdout)
csv_writer.writerow(
    ["group_id", "name", "description", "is_public", "default", "deleted"]
)
company = os.getenv("ZENDESK_COMPANY")
username = os.getenv("ZENDESK_USERNAME")
password = os.getenv("ZENDESK_PASSWORD")
z = zendesk.ZendeskClient(company, username, password)

for g in z.groups:
    csv_writer.writerow(
        [g.id, g.name, g.description, g.is_public, g.default, g.deleted]
    )
