import csv
import logging
import settings
import sys
import zendesk

log = logging.getLogger(__name__)


def get_external_ids(s: settings.Settings):
    result = {}
    with s.external_id_file.open(newline="") as f:
        for line in csv.DictReader(f):
            result[line.get("email").lower()] = line.get("external_id")
    return result


def main():
    s = settings.Settings()
    logging.basicConfig(format=s.log_format, level=logging.DEBUG, stream=sys.stdout)
    if not s.log_level == "DEBUG":
        log.debug(f"Changing log level to {s.log_level}")
    logging.getLogger().setLevel(s.log_level)

    log.info(f"Reading external_ids from {s.external_id_file}")
    external_ids = get_external_ids(s)
    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)

    for user in z.users:
        if user.suspended:
            log.info(f"{user.id} ({user.name}) is suspended")
            continue
        if user.external_id is None:
            if user.email in external_ids:
                external_id = external_ids.get(user.email)
                log.warning(
                    f"{user.id} ({user.name}) setting external_id to {external_id}"
                )
                user.external_id = external_id
            else:
                log.warning(
                    f"{user.id} ({user.name}) could not find external_id for {user.email}"
                )
        else:
            log.info(
                f"{user.id} ({user.name}) already has external_id: {user.external_id}"
            )


if __name__ == "__main__":
    main()
