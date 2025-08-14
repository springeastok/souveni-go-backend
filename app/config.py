from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # アプリケーション設定
    app_name: str = "SouveniGo"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # データベース設定
    database_url: str = ""
    
    # Azure SQL用（本番環境）
    database_server: str = ""
    database_name: str = ""
    database_username: str = ""
    database_password: str = ""
    database_driver: str = ""
    
    # JWT設定
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Azure Storage
    azure_storage_connection_string: str = ""
    azure_storage_container: str = ""
    
    class Config:
        env_file = ".env.local" if os.getenv("ENVIRONMENT", "development") == "development" else ".env.production"
    
    @property
    def get_database_url(self) -> str:
        """環境に応じたデータベースURLを返す"""
        if self.environment == "production":
            # Azure SQL Database
            return (
                f"mssql+pyodbc://{self.database_username}:{self.database_password}"
                f"@{self.database_server}/{self.database_name}"
                f"?driver={self.database_driver}&Encrypt=yes&TrustServerCertificate=no"
            )
        else:
            # SQLite（ローカル）
            return self.database_url or "sqlite:///./data/souvenigo.db"

@lru_cache()
def get_settings():
    return Settings()