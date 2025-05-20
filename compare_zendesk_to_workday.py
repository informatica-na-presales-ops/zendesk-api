import argparse
import csv
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-z", "--zendesk-file")
    parser.add_argument("-w", "--workday-file")
    return parser.parse_args()


def main():
    args = parse_args()
    csv_out = csv.writer(sys.stdout)
    csv_out.writerow(["email", "org", "in_workday"])
    with open(args.workday_file) as workday_file:
        workday_reader = csv.DictReader(workday_file)
        workday_users = []
        for row in workday_reader:
            email = row["Email Address"].split(" ")[0].lower()
            workday_users.append(email)
    with open(args.zendesk_file) as zendesk_file:
        zendesk_reader = csv.DictReader(zendesk_file)
        for row in zendesk_reader:
            csv_out.writerow(
                [
                    row["Email"],
                    row["Organization"],
                    str(row["Email"].lower() in workday_users),
                ]
            )


if __name__ == "__main__":
    main()
