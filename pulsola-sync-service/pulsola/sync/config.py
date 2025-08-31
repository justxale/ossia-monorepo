from ipaddress import IPv4Address

from pydantic import AmqpDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SyncServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    service_port: int
    service_workers: int = 1

    rabbit_host: IPv4Address | str
    rabbit_port: int
    rabbit_user: str
    rabbit_password: str

    @computed_field()  # type: ignore[prop-decorator]
    @property
    def rabbit_dsn(self) -> str:
        checked = AmqpDsn(
            f'amqp://{self.rabbit_user}:{self.rabbit_password}@{self.rabbit_host}:{self.rabbit_port}'
        )
        return str(checked)
