import os
import json
import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional, Annotated # Annotatedを追加

# --- データベース設定 ---
DB_FILENAME = "souveni_go.db"
DATABASE_URL = f"sqlite:///{DB_FILENAME}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app = FastAPI()

# --- CORS設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DBセッション ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydanticモデル定義 ---
class PreferenceVector(BaseModel):
    heritage_soul: int = 0; modern_heirloom: int = 0; folk_heart: int = 0; fresh_folk: int = 0; masterpiece: int = 0; innovative_classic: int = 0; craft_sense: int = 0; smart_craft: int = 0; signature_mood: int = 0; iconic_style: int = 0; local_trend: int = 0; playful_pop: int = 0; design_master: int = 0; global_trend: int = 0; smart_local: int = 0; smart_pick: int = 0

class Item(BaseModel):
    id: str
    name: str
    preferences: PreferenceVector

class SelectionResponse(BaseModel):
    suppliers: List[Item]
    products: List[Item]

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    age_group: Optional[str] = None
    gender: Optional[str] = None

class GuestPreferenceRequest(BaseModel):
    guest_id: str
    shown_items: List[Item]
    selected_ids: List[str]

class RegisteredUserPreferenceRequest(BaseModel):
    user_id: int
    shown_items: List[Item]
    selected_ids: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str
    email: str
    user_id: int

# --- APIエンドポイント定義 ---

@app.post("/users/register")
def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """新規ユーザー登録"""
    try:
        check_query = text("SELECT user_id FROM users WHERE email = :email")
        existing_user = db.execute(check_query, {"email": user_data.email}).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        insert_query = text(
            """
            INSERT INTO users (email, password_hash, age_group, gender, mode)
            VALUES (:email, :password, :age_group, :gender, 'registered')
            """
        )
        params = { "email": user_data.email, "password": user_data.password, "age_group": user_data.age_group, "gender": user_data.gender }
        result = db.execute(insert_query, params)
        db.commit()
        
        new_user_id = result.lastrowid
        return {"message": "User registered successfully", "user_id": new_user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/preferences/selection", response_model=SelectionResponse)
def get_items_for_selection(db: Session = Depends(get_db)):
    """ユーザーに提示するアイテムをランダムに6つ取得"""
    supplier_query = text("SELECT supplier_id, name, heritage_soul, modern_heirloom, folk_heart, fresh_folk, masterpiece, innovative_classic, craft_sense, smart_craft, signature_mood, iconic_style, local_trend, playful_pop, design_master, global_trend, smart_local, smart_pick FROM suppliers ORDER BY RANDOM() LIMIT 3")
    suppliers_result = db.execute(supplier_query).fetchall()
    product_query = text("SELECT product_code, name, heritage_soul, modern_heirloom, folk_heart, fresh_folk, masterpiece, innovative_classic, craft_sense, smart_craft, signature_mood, iconic_style, local_trend, playful_pop, design_master, global_trend, smart_local, smart_pick FROM products ORDER BY RANDOM() LIMIT 3")
    products_result = db.execute(product_query).fetchall()
    suppliers = [Item(id=f"s{row[0]}", name=row[1], preferences=PreferenceVector(**row._mapping)) for row in suppliers_result]
    products = [Item(id=row[0], name=row[1], preferences=PreferenceVector(**row._mapping)) for row in products_result]
    return SelectionResponse(suppliers=suppliers, products=products)

def calculate_preference_vector(shown_items: List[Item], selected_ids: List[str]) -> dict:
    """共通のpreference計算ロジック"""
    user_vector = np.zeros(16)
    preference_keys = PreferenceVector.model_fields.keys()
    selected_ids_set = set(selected_ids)

    for item in shown_items:
        item_vector = np.array([getattr(item.preferences, key) for key in preference_keys])
        if item.id in selected_ids_set:
            user_vector += item_vector
        else:
            user_vector -= (item_vector * 0.2)
    
    max_score = user_vector.max()
    final_vector = np.zeros(16, dtype=int) if max_score <= 0 else np.round((user_vector / max_score) * 100).astype(int)
    
    return dict(zip(preference_keys, final_vector))

@app.post("/users/preferences")
def save_registered_user_preferences(request: RegisteredUserPreferenceRequest, db: Session = Depends(get_db)):
    """登録ユーザーのpreferenceを計算・保存"""
    final_scores = calculate_preference_vector(request.shown_items, request.selected_ids)
    
    try:
        set_clause = ", ".join([f"{key} = :{key}" for key in final_scores.keys()])
        params = {"user_id": request.user_id, **final_scores}
        update_query = text(f"UPDATE users SET {set_clause} WHERE user_id = :user_id")
        result = db.execute(update_query, params)
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"User with ID {request.user_id} not found.")
        return {"message": "Preference score updated successfully.", "scores": final_scores}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/guests/preferences")
def save_guest_preferences(request: GuestPreferenceRequest, db: Session = Depends(get_db)):
    """ゲストのpreferenceを計算・保存"""
    final_scores = calculate_preference_vector(request.shown_items, request.selected_ids)
    
    try:
        insert_query = text(
            f"""
            INSERT INTO users (name, email, mode, {', '.join(final_scores.keys())})
            VALUES (:name, :email, 'guest', {', '.join(':' + k for k in final_scores.keys())})
            """
        )
        params = { "name": f"Guest {request.guest_id}", "email": f"{request.guest_id}@guest.local", **final_scores }
        result = db.execute(insert_query, params)
        db.commit()
        guest_user_id = result.lastrowid
        return {"message": "Guest preferences saved.", "guest_user_id": guest_user_id, "scores": final_scores}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# main.py

@app.post("/token", response_model=Token)
def login_for_access_token(
    # ★★★ デフォルト値のない引数を先に書く ★★★
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    # ★★★ デフォルト値のあるdb引数を一番最後に移動 ★★★
    db: Session = Depends(get_db)
):
    """メールアドレスとパスワードでユーザーを認証し、トークンを返す"""
    query = text("SELECT user_id, email, password_hash FROM users WHERE email = :email")
    user = db.execute(query, {"email": username}).first()

    if not user or user.password_hash != password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = "dummy_access_token"
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "email": user.email,
        "user_id": user.user_id
    }