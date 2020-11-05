import argparse
import csv
import logging
import pathlib
import settings
import sys
import zendesk

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('field_title')
    parser.add_argument('output_file')
    return parser.parse_args()


def main():
    s = settings.Settings()
    logging.basicConfig(format=s.log_format, level=logging.DEBUG, stream=sys.stdout)
    if not s.log_level == 'DEBUG':
        log.debug(f'Changing log level to {s.log_level}')
    logging.getLogger().setLevel(s.log_level)

    args = parse_args()

    log.info(f'Collecting options for ticket field: {args.field_title}')

    z = zendesk.ZendeskClient(s.zendesk_company, s.zendesk_username, s.zendesk_password)
    tf_options = []
    for tf in z.ticket_fields:
        if tf.title == args.field_title:
            for option in tf.options:
                tf_options.append({
                    'name': option.name,
                    'value': option.value
                })
    log.info(f'Found {len(tf_options)} options for {args.field_title}')

    output_file = pathlib.Path(args.output_file).resolve()
    log.info(f'Writing to {output_file}')
    with output_file.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'value'])
        writer.writeheader()
        writer.writerows(tf_options)


if __name__ == '__main__':
    main()
