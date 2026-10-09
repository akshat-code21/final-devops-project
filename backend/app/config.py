from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ExpensePilot API"
    database_url: str = "postgresql+psycopg://expensepilot:expensepilot@localhost:5432/expensepilot"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
