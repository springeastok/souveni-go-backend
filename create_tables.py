#!/usr/bin/env python3
"""
SQLiteデータベースのテーブル作成スクリプト
main.pyで使用されるテーブル構造に合わせて作成
"""
import sqlite3
import os
from datetime import datetime

# データベースファイル名（main.pyと同じ）
DB_FILENAME = "souveni_go.db"

def create_tables():
    """テーブルを作成する"""
    # データベース接続
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    
    try:
        print("テーブルを作成中...")
        
        # 1. usersテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                hashed_password TEXT,
                name TEXT,
                age TEXT,
                gender TEXT,
                mode TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                -- 嗜好スコア（PreferenceVector用）
                heritage_soul INTEGER DEFAULT 0,
                modern_heirloom INTEGER DEFAULT 0,
                folk_heart INTEGER DEFAULT 0,
                fresh_folk INTEGER DEFAULT 0,
                masterpiece INTEGER DEFAULT 0,
                innovative_classic INTEGER DEFAULT 0,
                craft_sense INTEGER DEFAULT 0,
                smart_craft INTEGER DEFAULT 0,
                signature_mood INTEGER DEFAULT 0,
                iconic_style INTEGER DEFAULT 0,
                local_trend INTEGER DEFAULT 0,
                playful_pop INTEGER DEFAULT 0,
                design_master INTEGER DEFAULT 0,
                global_trend INTEGER DEFAULT 0,
                smart_local INTEGER DEFAULT 0,
                smart_pick INTEGER DEFAULT 0
            )
        """)
        
        # 2. suppliersテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                address TEXT,
                hours TEXT,
                website TEXT,
                location TEXT NOT NULL,  -- JSON形式で保存
                city TEXT,
                phone_number TEXT,
                email TEXT,
                categories TEXT,  -- JSON形式で保存
                image_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                -- 嗜好スコア（PreferenceVector用）
                heritage_soul INTEGER DEFAULT 0,
                modern_heirloom INTEGER DEFAULT 0,
                folk_heart INTEGER DEFAULT 0,
                fresh_folk INTEGER DEFAULT 0,
                masterpiece INTEGER DEFAULT 0,
                innovative_classic INTEGER DEFAULT 0,
                craft_sense INTEGER DEFAULT 0,
                smart_craft INTEGER DEFAULT 0,
                signature_mood INTEGER DEFAULT 0,
                iconic_style INTEGER DEFAULT 0,
                local_trend INTEGER DEFAULT 0,
                playful_pop INTEGER DEFAULT 0,
                design_master INTEGER DEFAULT 0,
                global_trend INTEGER DEFAULT 0,
                smart_local INTEGER DEFAULT 0,
                smart_pick INTEGER DEFAULT 0
            )
        """)
        
        # 3. productsテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT UNIQUE NOT NULL,
                supplier_id INTEGER NOT NULL,
                maker TEXT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                category TEXT,
                image_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                -- 嗜好スコア（PreferenceVector用）
                heritage_soul INTEGER DEFAULT 0,
                modern_heirloom INTEGER DEFAULT 0,
                folk_heart INTEGER DEFAULT 0,
                fresh_folk INTEGER DEFAULT 0,
                masterpiece INTEGER DEFAULT 0,
                innovative_classic INTEGER DEFAULT 0,
                craft_sense INTEGER DEFAULT 0,
                smart_craft INTEGER DEFAULT 0,
                signature_mood INTEGER DEFAULT 0,
                iconic_style INTEGER DEFAULT 0,
                local_trend INTEGER DEFAULT 0,
                playful_pop INTEGER DEFAULT 0,
                design_master INTEGER DEFAULT 0,
                global_trend INTEGER DEFAULT 0,
                smart_local INTEGER DEFAULT 0,
                smart_pick INTEGER DEFAULT 0,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id)
            )
        """)
        
        # 4. favoritesテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                supplier_id INTEGER,
                product_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                UNIQUE(user_id, supplier_id, product_id)
            )
        """)
        
        # 5. destinatedテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS destinated (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                supplier_id INTEGER,
                product_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id),
                UNIQUE(user_id, supplier_id, product_id)
            )
        """)
        
        # コミット
        conn.commit()
        print("テーブルが正常に作成されました")
        
        # 作成されたテーブルを確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"作成されたテーブル: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        conn.rollback()
        
    finally:
        conn.close()

def verify_tables():
    """テーブルが正しく作成されたかを確認"""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    
    try:
        # 各テーブルの構造を確認
        tables = ['users', 'suppliers', 'products', 'favorites', 'destinated']
        
        for table in tables:
            print(f"\n--- {table}テーブル構造 ---")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  {column[1]} ({column[2]})")
                
    except Exception as e:
        print(f"確認中にエラーが発生: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"データベースファイル: {os.path.abspath(DB_FILENAME)}")
    print(f"現在のディレクトリ: {os.getcwd()}")
    
    create_tables()
    verify_tables()
    
    print("\n完了！これでmain.pyが正常に動作するはずです。")