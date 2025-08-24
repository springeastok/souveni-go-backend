#!/usr/bin/env python3
"""
外部SQLiteデータベースから現在のDBにデータを移行するスクリプト
"""
import sqlite3
import os

# 現在のデータベース
CURRENT_DB = "souveni_go.db"
# 移行元のデータベースファイルパス（ここを変更してください）
SOURCE_DB = "path/to/your_source_database.db"

def import_data_from_external_db(source_db_path):
    """外部データベースからデータを移行"""
    
    # ファイル存在確認
    if not os.path.exists(source_db_path):
        print(f"エラー: {source_db_path} が見つかりません")
        return False
        
    if not os.path.exists(CURRENT_DB):
        print(f"エラー: {CURRENT_DB} が見つかりません")
        return False
    
    print(f"移行元: {source_db_path}")
    print(f"移行先: {CURRENT_DB}")
    
    conn = sqlite3.connect(CURRENT_DB)
    cursor = conn.cursor()
    
    try:
        # 外部データベースをアタッチ
        cursor.execute(f"ATTACH DATABASE '{source_db_path}' AS source_db")
        print("外部データベースをアタッチしました")
        
        # 移行元のテーブル一覧を確認
        cursor.execute("SELECT name FROM source_db.sqlite_master WHERE type='table'")
        source_tables = [row[0] for row in cursor.fetchall()]
        print(f"移行元のテーブル: {source_tables}")
        
        # 現在のDBのテーブル一覧を確認
        cursor.execute("SELECT name FROM main.sqlite_master WHERE type='table'")
        current_tables = [row[0] for row in cursor.fetchall()]
        print(f"現在のDBのテーブル: {current_tables}")
        
        # 共通するテーブルを見つける
        common_tables = set(source_tables) & set(current_tables)
        print(f"共通するテーブル: {list(common_tables)}")
        
        if not common_tables:
            print("警告: 共通するテーブルがありません")
            print("手動でテーブル構造を確認してください")
            return False
        
        # 各テーブルのデータを移行
        for table in common_tables:
            if table == 'sqlite_sequence':
                continue  # システムテーブルはスキップ
                
            print(f"\n--- {table}テーブルを移行中 ---")
            
            # 移行元のデータ件数確認
            cursor.execute(f"SELECT COUNT(*) FROM source_db.{table}")
            source_count = cursor.fetchone()[0]
            print(f"移行元データ件数: {source_count}")
            
            if source_count == 0:
                print("データがないのでスキップします")
                continue
            
            # テーブル構造を確認（カラム名を取得）
            cursor.execute(f"PRAGMA source_db.table_info({table})")
            source_columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute(f"PRAGMA main.table_info({table})")
            current_columns = [col[1] for col in cursor.fetchall()]
            
            # 共通するカラムのみ移行
            common_columns = set(source_columns) & set(current_columns)
            if not common_columns:
                print(f"警告: {table}テーブルに共通するカラムがありません")
                continue
            
            columns_str = ", ".join(common_columns)
            print(f"移行するカラム: {columns_str}")
            
            # データを移行（重複を避けるため、存在確認してから挿入）
            if table == 'users' and 'email' in common_columns:
                # usersテーブルはemailで重複チェック
                cursor.execute(f"""
                    INSERT OR IGNORE INTO main.{table} ({columns_str})
                    SELECT {columns_str} FROM source_db.{table}
                """)
            elif table == 'suppliers' and 'name' in common_columns:
                # suppliersテーブルはnameで重複チェック
                cursor.execute(f"""
                    INSERT OR IGNORE INTO main.{table} ({columns_str})
                    SELECT {columns_str} FROM source_db.{table}
                """)
            elif table == 'products' and 'product_code' in common_columns:
                # productsテーブルはproduct_codeで重複チェック
                cursor.execute(f"""
                    INSERT OR IGNORE INTO main.{table} ({columns_str})
                    SELECT {columns_str} FROM source_db.{table}
                """)
            else:
                # その他のテーブルは単純に挿入
                cursor.execute(f"""
                    INSERT INTO main.{table} ({columns_str})
                    SELECT {columns_str} FROM source_db.{table}
                """)
            
            migrated_count = cursor.rowcount
            print(f"移行完了: {migrated_count}件")
        
        # アタッチを解除
        cursor.execute("DETACH DATABASE source_db")
        
        # コミット
        conn.commit()
        print("\nデータ移行が完了しました！")
        
        # 結果確認
        print("\n--- 移行後のデータ件数 ---")
        for table in common_tables:
            if table == 'sqlite_sequence':
                continue
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count}件")
        
        return True
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def preview_source_db(source_db_path):
    """移行元データベースの内容を確認"""
    if not os.path.exists(source_db_path):
        print(f"ファイルが見つかりません: {source_db_path}")
        return
        
    conn = sqlite3.connect(source_db_path)
    cursor = conn.cursor()
    
    try:
        print(f"\n--- {source_db_path} の内容 ---")
        
        # テーブル一覧
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name == 'sqlite_sequence':
                continue
                
            # データ件数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # テーブル構造
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            print(f"\nテーブル: {table_name}")
            print(f"  データ件数: {count}")
            print(f"  カラム: {', '.join(columns)}")
            
            # サンプルデータ（最初の3件）
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()
                print(f"  サンプル: {len(samples)}件")
                
    finally:
        conn.close()

if __name__ == "__main__":
    print("SQLiteデータベース移行スクリプト")
    print("=" * 50)
    
    # 移行元ファイルパスを入力
    source_file = input("移行元のDBファイルパスを入力してください: ").strip()
    
    if not source_file:
        print("ファイルパスが入力されていません")
        exit(1)
    
    # プレビュー
    preview_source_db(source_file)
    
    # 確認
    confirm = input(f"\n{source_file} から {CURRENT_DB} にデータを移行しますか？ (y/N): ").strip().lower()
    
    if confirm == 'y':
        success = import_data_from_external_db(source_file)
        if success:
            print("移行完了！")
        else:
            print("移行に失敗しました")
    else:
        print("移行をキャンセルしました")