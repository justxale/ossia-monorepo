import os
from ipaddress import IPv4Address
from urllib.parse import quote_plus

from pydantic import AmqpDsn, HttpUrl, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UserServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    service_port: int
    secure: bool

    rabbit_host: IPv4Address | str
    rabbit_port: int
    rabbit_user: str
    rabbit_password: str

    s3_host: IPv4Address | str
    s3_port: int
    s3_access_key: str
    s3_secret_key: str

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    jwt_secret_key: str
    jwt_ttl_hours: int

    @computed_field()
    @property
    def rabbit_dsn(self) -> str:
        checked = AmqpDsn(f"amqp://{self.rabbit_user}:{self.rabbit_password}@{self.rabbit_host}:{self.rabbit_port}")
        return str(checked)

    @computed_field()
    @property
    def s3_url(self) -> str:
        if self.secure:
            checked = HttpUrl(f"https://{self.s3_host}:{self.s3_port}")
        else:
            checked = HttpUrl(f"http://{self.s3_host}:{self.s3_port}")
        return str(checked)

    @computed_field()
    @property
    def postgres_url(self) -> str:
        checked = PostgresDsn(
            f"postgres://{self.postgres_user}:{quote_plus(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return str(checked)

    @computed_field()
    @property
    def jwt_ttl_seconds(self) -> int:
        return self.jwt_ttl_hours * 60 * 60
