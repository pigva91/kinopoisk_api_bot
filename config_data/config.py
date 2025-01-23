from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class SiteSettings(BaseSettings):
    API_KEY: SecretStr
    API_URL: str = "https://api.kinopoisk.dev/v1.4/movie"
    BOT_TOKEN: SecretStr

    class Config:
        env_file = "../.env"


settings = SiteSettings()
