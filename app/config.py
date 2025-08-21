from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_min: int
    refresh_token_expire_day: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port:int
    cloud_name: str
    api_key: str
    api_secret: str

    class Config:
        env_file = ".env"

settings = Settings()
