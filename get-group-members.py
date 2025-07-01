import dotenv
import logging
import notch
import os
import settings
import zendesk

dotenv.load_dotenv(".local/.env")
notch.configure()

log = logging.getLogger(__name__)


def main():
    s = settings.Settings()
    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)
    group_id = int(os.getenv("GROUP_ID"))
    m = list(z.list_memberships_for_group(group_id))
    log.info(f"Found {len(m)} memberships for group {group_id}")
    for x in m:
        u = z.get_user_by_id(x.user_id)
        print(u.email)


if __name__ == "__main__":
    main()
