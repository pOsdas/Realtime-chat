from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Принудительно загружаем .env и .env-template
load_dotenv(encoding="utf-8")


class RunModel(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8005


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "api"
    v1: ApiV1Prefix = ApiV1Prefix()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env-template", ".env"),
        case_sensitive=False,
        extra="ignore",
    )
    # postgres
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    pgdata: str

    # db
    allow_db_create: int
    db_create_retry_delay: int
    db_create_retries: int

    # django
    django_settings_module: str

    # backend
    debug: bool = False
    secret_key: str
    allowed_hosts: str

    # redis
    redis_host: str
    redis_port: str
    redis_db: int

    # docker
    docker: bool = False

    # other
    run: RunModel = RunModel()
    api: ApiPrefix = ApiPrefix()


pydantic_settings = Settings()
# pprint(pydantic_settings.model_dump())
