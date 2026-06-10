from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str

    MELI_APP_ID: str = ""
    MELI_CLIENT_ID: str = ""
    MELI_CLIENT_SECRET: str = ""
    MELI_REDIRECT_URI: str = ""
    MELI_SITE_ID: str = "MLC"
    MELI_CATEGORY_ID: str = "MLC455614"

    IMAGE_LIBRARY_PATH: str = "./imagenes"
    DEFAULT_STOCK: int = 100
    DEFAULT_BRAND: str = "Genérica"

    FALABELLA_API_URL: str = "https://sellercenter-api.falabella.com/"
    FALABELLA_USER_ID: str = ""
    FALABELLA_API_KEY: str = ""
    FALABELLA_VERSION: str = "1.0"
    FALABELLA_FORMAT: str = "JSON"
    FALABELLA_OPERATOR: str = "facl"


settings = Settings()