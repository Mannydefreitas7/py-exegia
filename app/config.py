from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)

	# Supabase
	supabase_url: str = ""
	supabase_anon_key: str = ""
	supabase_service_role_key: str = ""
	supabase_storage_bucket: str = "biblepedia-data"

	# Database (Supabase PostgreSQL connection string)
	database_url: str = "postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.vjkvpoemqigobzogmrrx.supabase.co:5432/postgres"

	# App
	environment: str = "development"
	cors_origins: str = "http://localhost:5173,http://localhost:3000"

	@property
	def cors_origins_list(self) -> list[str]:
		return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

	@property
	def is_development(self) -> bool:
		return self.environment == "development"


settings = Settings()
