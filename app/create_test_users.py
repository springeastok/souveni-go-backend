import os
import sqlite3
import random

# --- 設定 ---
DB_FILENAME = "souveni_go.db"
NUM_USERS = 5 # 作成/更新するユーザー数

# 年齢層と性別の選択肢を定義
ageS = ['18-25', '26-35', '36-45', '46-55', '56+']
GENDERS = ['male', 'female', 'other', 'prefer-not-to-say']
# ★★★ modeカラム用のデフォルト値を追加 ★★★
DEFAULT_MODE = 'explore' 

def create_or_update_test_users():
    """
    テストユーザーを作成、または既存のユーザー情報を更新する。
    modeカラムにもデフォルト値を設定する。
    """
    print(f"--- Creating or updating test users in '{DB_FILENAME}' ---")
    
    if not os.path.exists(DB_FILENAME):
        print(f"❌ ERROR: Database file '{DB_FILENAME}' not found.")
        return

    try:
        conn = sqlite3.connect(DB_FILENAME)
        cursor = conn.cursor()

        for i in range(1, NUM_USERS + 1):
            # 挿入/更新するデータを生成
            user_name = f"Test User T{i:03d}"
            user_email = f"testuser{i}@example.com"
            random_age = random.choice(ageS)
            random_gender = random.choice(GENDERS)
            
            print(f"  - Processing: {user_name}, email: {user_email}, mode: {DEFAULT_MODE}")

            # ★★★ SQL文に 'mode' を追加 ★★★
            cursor.execute(
                """
                INSERT INTO users (name, email, age, gender, mode) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    name = excluded.name,
                    age = excluded.age,
                    gender = excluded.gender,
                    mode = excluded.mode
                """,
                (user_name, user_email, random_age, random_gender, DEFAULT_MODE)
            )

        conn.commit()
        print(f"\n✅ Process complete. {NUM_USERS} test users are now created or updated.")

    except sqlite3.Error as e:
        print(f"❌ An error occurred with the database: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_or_update_test_users()