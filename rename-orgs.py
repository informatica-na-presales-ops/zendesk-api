import logging
import settings
import sys
import zendesk

log = logging.getLogger("zendesk_api.rename_orgs")


def main():
    s = settings.Settings()
    logging.basicConfig(format=s.log_format, level=logging.DEBUG, stream=sys.stdout)
    if not s.log_level == "DEBUG":
        log.debug(f"Changing log level to {s.log_level}")
    logging.getLogger().setLevel(s.log_level)

    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)
    for org in z.organizations:
        if "Presales" in org.name:
            org.name = org.name.replace("Presales", "PreSales")


if __name__ == "__main__":
    main()
