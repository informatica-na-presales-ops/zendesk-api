import csv
import logging
import os
import pathlib
import sys
import zendesk

log = logging.getLogger(__name__)


class Settings:
    @property
    def external_id_file(self) -> pathlib.Path:
        return pathlib.Path(os.getenv('EXTERNAL_ID_FILE', '/data.csv')).resolve()

    @property
    def log_format(self) -> str:
        return os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')

    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')

    @property
    def zendesk_company(self) -> str:
        return os.getenv('ZENDESK_COMPANY')

    @property
    def zendesk_password(self) -> str:
        return os.getenv('ZENDESK_PASSWORD')

    @property
    def zendesk_username(self) -> str:
        return os.getenv('ZENDESK_USERNAME')


def get_external_ids(settings: Settings):
    result = {}
    with settings.external_id_file.open(newline='') as f:
        for line in csv.DictReader(f):
            result[line.get('email').lower()] = line.get('employee_id')
    return result


def main():
    settings = Settings()
    logging.basicConfig(format=settings.log_format, level=logging.DEBUG, stream=sys.stdout)
    if not settings.log_level == 'DEBUG':
        log.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    log.info(f'Reading external_ids from {settings.external_id_file}')
    external_ids = get_external_ids(settings)
    z = zendesk.ZendeskClient(settings.zendesk_company, settings.zendesk_username, settings.zendesk_password)

    for user in z.users:
        if user.external_id is None:
            if user.email in external_ids:
                external_id = external_ids.get(user.email)
                log.warning(f'{user.id} ({user.name}) setting external_id to {external_id}')
                user.external_id = external_id
            else:
                log.warning(f'{user.id} ({user.name}) could not find external_id for {user.email}')
        else:
            log.info(f'{user.id} ({user.name}) already has external_id: {user.external_id}')


if __name__ == '__main__':
    main()
