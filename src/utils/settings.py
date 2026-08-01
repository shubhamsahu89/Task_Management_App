from pydantic_settings import BaseSettings ,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

    DB_CONNECTIONS:str
    SECRET_KEY:str
    ALGORITHM:str
    EXP_TIME:int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str


settings=Settings()