import os
import pathlib


class Settings:
    @property
    def external_id_file(self) -> pathlib.Path:
        return pathlib.Path(os.getenv("EXTERNAL_ID_FILE", "/data.csv")).resolve()

    @property
    def log_format(self) -> str:
        return os.getenv("LOG_FORMAT", "%(levelname)s [%(name)s] %(message)s")

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def zendesk_company(self) -> str:
        return os.getenv("ZENDESK_COMPANY")

    @property
    def zendesk_password(self) -> str:
        return os.getenv("ZENDESK_PASSWORD")

    @property
    def zendesk_username(self) -> str:
        return os.getenv("ZENDESK_USERNAME")
