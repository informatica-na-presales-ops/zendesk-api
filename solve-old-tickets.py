import datetime
import logging
import readline
import requests
import settings
import sys
import zendesk

log = logging.getLogger("zendesk_api.solve_old_tickets")


def main():
    s = settings.Settings()
    logging.basicConfig(format=s.log_format, level=logging.DEBUG, stream=sys.stdout)
    if not s.log_level == "DEBUG":
        log.debug(f"Changing log level to {s.log_level}")
    logging.getLogger().setLevel(s.log_level)

    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)
    query = f"type:ticket status<solved updated<{datetime.date.today() - datetime.timedelta(days=366)}"
    data = z.search(query, sort_by="updated_at", sort_order="asc")
    succeeded = 0
    for result in data.get("results", []):
        ticket_id = result.get("id")
        subject = result.get("subject")
        updated_at = result.get("updated_at")[:10]
        log.info(f"{ticket_id} / {subject} / updated {updated_at}")
        params = {"status": "solved"}
        for cf in result.get("custom_fields", []):
            if cf.get("id") == 360000398388:
                if cf.get("value") is None:
                    params.update(
                        {
                            "custom_fields": [
                                {
                                    "id": 360000398388,
                                    "value": "complete_and_high_quality",
                                }
                            ]
                        }
                    )
                break
        try:
            z.update_ticket(ticket_id, params)
            succeeded += 1
        except requests.exceptions.HTTPError as e:
            log.error(e)
    log.info(f"Succeeded: {succeeded}")


if __name__ == "__main__":
    main()
