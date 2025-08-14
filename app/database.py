from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import os

settings = get_settings()

# 環境に応じたエンジン設定
if settings.environment == "production":
    # Azure SQL Database用
    engine = create_engine(
        settings.get_database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
else:
    # SQLite用（ローカル）
    # データフォルダが存在しない場合は作成
    os.makedirs("data", exist_ok=True)
    
    engine = create_engine(
        settings.get_database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False}  # SQLite用の設定
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """データベースの初期化（テーブル作成）"""
    import app.models  # すべてのモデルをインポート
    Base.metadata.create_all(bind=engine)