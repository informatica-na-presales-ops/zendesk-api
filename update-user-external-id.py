import logging
import os
import sys
import zendesk

log = logging.getLogger(__name__)


class Settings:
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


def main():
    settings = Settings()
    logging.basicConfig(format=settings.log_format, level=logging.DEBUG, stream=sys.stdout)
    if not settings.log_level == 'DEBUG':
        log.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    z = zendesk.ZendeskClient(settings.zendesk_company, settings.zendesk_username, settings.zendesk_password)
    for user in z.users:
        log.info(user)
        break


if __name__ == '__main__':
    main()
