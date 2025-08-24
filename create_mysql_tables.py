#!/usr/bin/env python3
"""
Azure MySQL用のテーブル作成スクリプト
SQLiteのテーブル構造をMySQL形式に変換
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def get_mysql_engine():
    """MySQL接続エンジンを取得"""
    host = os.getenv('MYSQL_HOST')
    port = os.getenv('MYSQL_PORT', '3306')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DATABASE')
    
    if not all([host, user, password, database]):
        print("エラー: MySQL接続情報が設定されていません")
        print(".envファイルで以下の変数を設定してください:")
        print("- MYSQL_HOST")
        print("- MYSQL_USER") 
        print("- MYSQL_PASSWORD")
        print("- MYSQL_DATABASE")
        return None
    
    # Azure MySQLの接続URL（SSL設定を調整）
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4&ssl=true&ssl_verify_cert=false&ssl_verify_identity=false"
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        print(f"MySQL接続エラー: {e}")
        return None

def create_mysql_tables():
    """MySQLにテーブルを作成"""
    engine = get_mysql_engine()
    if not engine:
        return False
    
    print("MySQLにテーブルを作成中...")
    
    try:
        with engine.connect() as conn:
            # 1. usersテーブル作成
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE,
                    hashed_password VARCHAR(255),
                    name VARCHAR(100),
                    age VARCHAR(20),
                    gender VARCHAR(10),
                    mode VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    -- 嗜好スコア（PreferenceVector用）
                    heritage_soul INT DEFAULT 0,
                    modern_heirloom INT DEFAULT 0,
                    folk_heart INT DEFAULT 0,
                    fresh_folk INT DEFAULT 0,
                    masterpiece INT DEFAULT 0,
                    innovative_classic INT DEFAULT 0,
                    craft_sense INT DEFAULT 0,
                    smart_craft INT DEFAULT 0,
                    signature_mood INT DEFAULT 0,
                    iconic_style INT DEFAULT 0,
                    local_trend INT DEFAULT 0,
                    playful_pop INT DEFAULT 0,
                    design_master INT DEFAULT 0,
                    global_trend INT DEFAULT 0,
                    smart_local INT DEFAULT 0,
                    smart_pick INT DEFAULT 0,
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # 2. suppliersテーブル作成
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    address VARCHAR(500),
                    hours VARCHAR(255),
                    website VARCHAR(500),
                    location JSON NOT NULL,
                    city VARCHAR(100),
                    phone_number VARCHAR(20),
                    email VARCHAR(255),
                    categories JSON,
                    image_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    -- 嗜好スコア（PreferenceVector用）
                    heritage_soul INT DEFAULT 0,
                    modern_heirloom INT DEFAULT 0,
                    folk_heart INT DEFAULT 0,
                    fresh_folk INT DEFAULT 0,
                    masterpiece INT DEFAULT 0,
                    innovative_classic INT DEFAULT 0,
                    craft_sense INT DEFAULT 0,
                    smart_craft INT DEFAULT 0,
                    signature_mood INT DEFAULT 0,
                    iconic_style INT DEFAULT 0,
                    local_trend INT DEFAULT 0,
                    playful_pop INT DEFAULT 0,
                    design_master INT DEFAULT 0,
                    global_trend INT DEFAULT 0,
                    smart_local INT DEFAULT 0,
                    smart_pick INT DEFAULT 0,
                    INDEX idx_name (name),
                    INDEX idx_city (city)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # 3. productsテーブル作成
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INT AUTO_INCREMENT PRIMARY KEY,
                    product_code VARCHAR(50) UNIQUE NOT NULL,
                    supplier_id INT NOT NULL,
                    maker VARCHAR(255),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2),
                    category VARCHAR(100),
                    image_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    -- 嗜好スコア（PreferenceVector用）
                    heritage_soul INT DEFAULT 0,
                    modern_heirloom INT DEFAULT 0,
                    folk_heart INT DEFAULT 0,
                    fresh_folk INT DEFAULT 0,
                    masterpiece INT DEFAULT 0,
                    innovative_classic INT DEFAULT 0,
                    craft_sense INT DEFAULT 0,
                    smart_craft INT DEFAULT 0,
                    signature_mood INT DEFAULT 0,
                    iconic_style INT DEFAULT 0,
                    local_trend INT DEFAULT 0,
                    playful_pop INT DEFAULT 0,
                    design_master INT DEFAULT 0,
                    global_trend INT DEFAULT 0,
                    smart_local INT DEFAULT 0,
                    smart_pick INT DEFAULT 0,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
                    INDEX idx_product_code (product_code),
                    INDEX idx_supplier_id (supplier_id),
                    INDEX idx_category (category)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # 4. favoritesテーブル作成
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    supplier_id INT,
                    product_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
                    UNIQUE KEY unique_favorite (user_id, supplier_id, product_id),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # 5. destinatedテーブル作成
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS destinated (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    supplier_id INT,
                    product_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
                    UNIQUE KEY unique_destinated (user_id, supplier_id, product_id),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # コミット
            conn.commit()
            print("MySQLテーブルが正常に作成されました")
            
            # 作成されたテーブルを確認
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"作成されたテーブル: {tables}")
            
            return True
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

def test_connection():
    """MySQL接続テスト"""
    engine = get_mysql_engine()
    if not engine:
        return False
        
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION() as version"))
            version = result.fetchone()[0]
            print(f"MySQL接続成功: {version}")
            return True
    except Exception as e:
        print(f"MySQL接続失敗: {e}")
        return False

if __name__ == "__main__":
    print("Azure MySQL テーブル作成スクリプト")
    print("=" * 50)
    
    print("1. 接続テスト中...")
    if not test_connection():
        print("接続に失敗しました。.envファイルの設定を確認してください。")
        sys.exit(1)
    
    print("2. テーブル作成中...")
    if create_mysql_tables():
        print("\n完了！これでAzure MySQLが使用可能です。")
    else:
        print("テーブル作成に失敗しました。")
        sys.exit(1)