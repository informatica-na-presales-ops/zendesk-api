import csv
import html.parser
import notch
import pathlib
import settings
import zendesk

notch.configure()


class MajorCertParser(html.parser.HTMLParser):
    email: str = None
    href: str = None
    in_h5: bool = False

    def handle_data(self, data):
        if self.in_h5 and self.email is None:
            tokens = data.split()
            self.email = tokens[-1]

    def handle_endtag(self, tag):
        if tag == "h5":
            self.in_h5 = False

    def handle_starttag(self, tag, attrs):
        if tag == "h5":
            self.in_h5 = True
        elif tag == "a" and self.href is None:
            for name, value in attrs:
                if name == "href":
                    self.href = value


def main():
    s = settings.Settings()
    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)
    query = 'subject:"Major certification request for"'
    out = pathlib.Path("major-cert-tickets.csv")
    with out.open(mode="w", newline="") as f:
        csv_file = csv.writer(f)
        csv_file.writerow(["id", "subject", "created_at", "submitter", "video_url"])
        for t in z.search_tickets(query, "created_at", "asc"):
            for c in t.comments:
                parser = MajorCertParser()
                parser.feed(c.html_body)
                csv_file.writerow(
                    [t.id, t.subject, t.created_at, parser.email, parser.href]
                )
                break


if __name__ == "__main__":
    main()
