import argparse
import logging
import notch
import settings
import zendesk

notch.configure()
log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    return parser.parse_args()


def main():
    args = parse_args()
    s = settings.Settings()
    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)
    query = f"type:ticket status<solved cc:{args.email}"
    data = z.search(query)
    for result in data.get("results", []):
        ticket_id = result.get("id")
        log.info(f"Found a ticket: {ticket_id}")
        go = input(f"Do you want to remove {args.email} from the ticket email_ccs? ")
        if go.lower() == "y":
            t = zendesk.ZendeskTicket(z, id=ticket_id)
            response = t.remove_email_cc(args.email)
            log.debug(response)


if __name__ == "__main__":
    main()
