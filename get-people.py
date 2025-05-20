import csv
import os
import sys
import zendesk


def main():
    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow(
        [
            "user_id",
            "name",
            "employee_id",
            "active",
            "verified",
            "last_login_at",
            "email",
            "organizations",
            "role",
            "agent_groups",
            "restricted_agent",
            "ticket_restriction",
            "suspended",
            "org_tags",
        ]
    )
    company = os.getenv("ZENDESK_COMPANY")
    username = os.getenv("ZENDESK_USERNAME")
    password = os.getenv("ZENDESK_PASSWORD")
    z = zendesk.ZendeskClient(company, username, password)

    for user in z.users:
        org_names = "|".join(sorted([o.name for o in user.organizations]))
        group_names = "|".join(sorted([g.name for g in user.groups]))
        org_tags = set()
        for o in user.organizations:
            org_tags.update(o.tags)
        org_tags = "|".join(sorted(org_tags))
        csv_writer.writerow(
            [
                user.id,
                user.name,
                user.external_id,
                user.active,
                user.verified,
                user.last_login_at,
                user.email,
                org_names,
                user.role,
                group_names,
                user.restricted_agent,
                user.ticket_restriction,
                user.suspended,
                org_tags,
            ]
        )


if __name__ == "__main__":
    main()
