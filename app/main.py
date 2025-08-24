import os
import json
import math
import numpy as np
import traceback 
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from dotenv import load_dotenv

# 環境変数を読み込み（.envファイルが存在する場合のみ）
try:
    load_dotenv()
except Exception:
    # Azure App Service等では.envファイルがないため、環境変数から直接読み込み
    pass

# --- データベース設定 ---
def get_database_url():
    """環境に応じたデータベースURL を取得"""
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    
    if dev_mode:
        # 開発環境：SQLite
        return f"sqlite:///souveni_go.db"
    else:
        # 本番環境：Azure MySQL
        host = os.getenv('MYSQL_HOST')
        port = os.getenv('MYSQL_PORT', '3306')
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        
        if not all([host, user, password, database]):
            raise ValueError("MySQL接続情報が設定されていません。.envファイルを確認してください。")
        
        # Azure MySQLの接続URL（SSL設定を調整）
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4&ssl=true&ssl_verify_cert=false&ssl_verify_identity=false"

DATABASE_URL = get_database_url()

# SQLite用の設定はMySQLでは不要
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
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
    description: Optional[str] = None
    image_url: Optional[str] = None
    preferences: PreferenceVector

class UserRegisterRequest(BaseModel):
    email: str; password: str
    age: Optional[str] = None
    gender: Optional[str] = None

class ProfileSetupRequest(BaseModel):
    user_id: Optional[int] = None; guest_id: Optional[str] = None
    age: str
    gender: str

class PreferenceRequest(BaseModel):
    user_id: int; shown_items: List[Item]; selected_ids: List[str]

class Token(BaseModel):
    access_token: str; token_type: str; email: str; user_id: int

class Location(BaseModel):
    lat: float
    lng: float

class RecommendationItem(Item):
    location: Optional[Location] = None
    match_score: int = Field(..., ge=0, le=100)
    distance_km: Optional[float] = None

class SelectionResponse(BaseModel):
    suppliers: List[Item]
    products: List[Item]

class RecommendationResponse(BaseModel):
    items: List[RecommendationItem]

class FavoriteRequest(BaseModel):
    user_id: int
    item_id: str

class DestinatedRequest(BaseModel):
    user_id: int
    item_id: str

# --- ヘルパー関数 ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_preference_vector(shown_items: List[Item], selected_ids: List[str]) -> dict:
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
    
    final_scores_dict = dict(zip(preference_keys, final_vector))
    return {key: int(value) for key, value in final_scores_dict.items()}

# --- APIエンドポイント定義 ---
@app.post("/users/register")
def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        check_query = text("SELECT user_id FROM users WHERE email = :email")
        if db.execute(check_query, {"email": user_data.email}).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        insert_query = text("INSERT INTO users (email, hashed_password, age, gender, mode) VALUES (:email, :password, :age, :gender, 'registered')")
        params = {"email": user_data.email, "password": user_data.password, "age": user_data.age, "gender": user_data.gender}
        result = db.execute(insert_query, params)
        db.commit()
        return {"message": "User registered successfully", "user_id": result.lastrowid}
    except Exception as e:
        db.rollback(); raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/profile")
def setup_user_profile(request: ProfileSetupRequest, db: Session = Depends(get_db)):
    if request.user_id:
        try:
            update_query = text("UPDATE users SET age = :age, gender = :gender WHERE user_id = :uid")
            params = {"age": request.age, "gender": request.gender, "uid": request.user_id}
            result = db.execute(update_query, params)
            db.commit()
            if result.rowcount == 0: raise HTTPException(status_code=404, detail="User not found")
            return {"message": "Profile updated", "user_id": request.user_id}
        except Exception as e:
            db.rollback(); raise HTTPException(status_code=500, detail=str(e))
    elif request.guest_id:
        try:
            guest_email = f"{request.guest_id}@guest.local"
            check_query = text("SELECT user_id FROM users WHERE email = :email AND mode = 'guest'")
            existing_guest = db.execute(check_query, {"email": guest_email}).first()
            if existing_guest:
                update_query = text("UPDATE users SET age = :age, gender = :gender WHERE user_id = :uid")
                params = {"age": request.age, "gender": request.gender, "uid": existing_guest.user_id}
                db.execute(update_query, params)
                db.commit()
                return {"message": "Guest profile updated", "user_id": existing_guest.user_id}
            else:
                insert_query = text("INSERT INTO users (name, email, age, gender, mode, hashed_password) VALUES (:name, :email, :age, :gender, 'guest', 'guest_user')")
                params = {"name": f"Guest {request.guest_id}", "email": guest_email, "age": request.age, "gender": request.gender}
                result = db.execute(insert_query, params)
                db.commit()
                return {"message": "Guest user created", "user_id": result.lastrowid}
        except Exception as e:
            db.rollback(); raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=400, detail="user_id or guest_id must be provided")

@app.get("/preferences/selection", response_model=SelectionResponse)
def get_items_for_selection(db: Session = Depends(get_db)):
    supplier_query = text("SELECT supplier_id, name, description, image_url, heritage_soul, modern_heirloom, folk_heart, fresh_folk, masterpiece, innovative_classic, craft_sense, smart_craft, signature_mood, iconic_style, local_trend, playful_pop, design_master, global_trend, smart_local, smart_pick FROM suppliers ORDER BY RAND() LIMIT 3")
    suppliers_result = db.execute(supplier_query).fetchall()
    product_query = text("SELECT product_code, name, description, image_url, heritage_soul, modern_heirloom, folk_heart, fresh_folk, masterpiece, innovative_classic, craft_sense, smart_craft, signature_mood, iconic_style, local_trend, playful_pop, design_master, global_trend, smart_local, smart_pick FROM products ORDER BY RAND() LIMIT 3")
    products_result = db.execute(product_query).fetchall()
    # Suppliersの変換（_mappingの代わりに個別のカラムを指定）
    suppliers = []
    for row in suppliers_result:
        pref_dict = {
            'heritage_soul': row.heritage_soul or 0,
            'modern_heirloom': row.modern_heirloom or 0,
            'folk_heart': row.folk_heart or 0,
            'fresh_folk': row.fresh_folk or 0,
            'masterpiece': row.masterpiece or 0,
            'innovative_classic': row.innovative_classic or 0,
            'craft_sense': row.craft_sense or 0,
            'smart_craft': row.smart_craft or 0,
            'signature_mood': row.signature_mood or 0,
            'iconic_style': row.iconic_style or 0,
            'local_trend': row.local_trend or 0,
            'playful_pop': row.playful_pop or 0,
            'design_master': row.design_master or 0,
            'global_trend': row.global_trend or 0,
            'smart_local': row.smart_local or 0,
            'smart_pick': row.smart_pick or 0
        }
        suppliers.append(Item(
            id=f"s{row.supplier_id}",
            name=row.name,
            description=row.description,
            image_url=row.image_url,
            preferences=PreferenceVector(**pref_dict)
        ))
    
    # Productsの変換（_mappingの代わりに個別のカラムを指定）
    products = []
    for row in products_result:
        pref_dict = {
            'heritage_soul': row.heritage_soul or 0,
            'modern_heirloom': row.modern_heirloom or 0,
            'folk_heart': row.folk_heart or 0,
            'fresh_folk': row.fresh_folk or 0,
            'masterpiece': row.masterpiece or 0,
            'innovative_classic': row.innovative_classic or 0,
            'craft_sense': row.craft_sense or 0,
            'smart_craft': row.smart_craft or 0,
            'signature_mood': row.signature_mood or 0,
            'iconic_style': row.iconic_style or 0,
            'local_trend': row.local_trend or 0,
            'playful_pop': row.playful_pop or 0,
            'design_master': row.design_master or 0,
            'global_trend': row.global_trend or 0,
            'smart_local': row.smart_local or 0,
            'smart_pick': row.smart_pick or 0
        }
        products.append(Item(
            id=row.product_code,
            name=row.name,
            description=row.description,
            image_url=row.image_url,
            preferences=PreferenceVector(**pref_dict)
        ))
    return SelectionResponse(suppliers=suppliers, products=products)

@app.post("/users/preferences")
def save_preferences(request: PreferenceRequest, db: Session = Depends(get_db)):
    final_scores = calculate_preference_vector(request.shown_items, request.selected_ids)
    try:
        set_clause = ", ".join([f"{key} = :{key}" for key in final_scores.keys()])
        params = {"user_id": request.user_id, **final_scores}
        update_query = text(f"UPDATE users SET {set_clause} WHERE user_id = :user_id")
        result = db.execute(update_query, params)
        db.commit()
        if result.rowcount == 0: raise HTTPException(status_code=404, detail=f"User with ID {request.user_id} not found.")
        return {"message": "Preference score updated successfully.", "scores": final_scores}
    except Exception as e:
        db.rollback(); raise HTTPException(status_code=500, detail=str(e))

@app.post("/token", response_model=Token)
def login_for_access_token(username: Annotated[str, Form()], password: Annotated[str, Form()], db: Session = Depends(get_db)):
    query = text("SELECT user_id, email, hashed_password FROM users WHERE email = :email")
    user = db.execute(query, {"email": username}).first()
    if not user or user.hashed_password != password:
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": "dummy_token", "token_type": "bearer", "email": user.email, "user_id": user.user_id}

@app.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(user_id: int, latitude: float, longitude: float, db: Session = Depends(get_db)):
    user_result = db.execute(text("SELECT * FROM users WHERE user_id = :uid"), {"uid": user_id}).first()
    if not user_result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_prefs_dict = {key: getattr(user_result, key, 0) for key in PreferenceVector.model_fields.keys()}
    user_vector = np.array(list(user_prefs_dict.values()))

    # ★★★ 1. p.product_code をSELECT文に追加 ★★★
    query = text("""
        SELECT
            p.product_id, p.product_code, p.name AS product_name, p.description, p.image_url,
            s.location,
            p.heritage_soul, p.modern_heirloom, p.folk_heart, p.fresh_folk, 
            p.masterpiece, p.innovative_classic, p.craft_sense, p.smart_craft, 
            p.signature_mood, p.iconic_style, p.local_trend, p.playful_pop, 
            p.design_master, p.global_trend, p.smart_local, p.smart_pick
        FROM products p
        JOIN suppliers s ON p.supplier_id = s.supplier_id
    """)
    all_products = db.execute(query).fetchall()

    recommendations = []
    for product in all_products:
        supplier_location = json.loads(product.location) if isinstance(product.location, str) else product.location
        if not supplier_location or 'lat' not in supplier_location or 'lng' not in supplier_location:
            continue

        distance = haversine_distance(latitude, longitude, supplier_location['lat'], supplier_location['lng'])
        if distance > 10:
            continue
            
        product_prefs_dict = {key: getattr(product, key, 0) for key in PreferenceVector.model_fields.keys()}
        product_vector = np.array(list(product_prefs_dict.values()))
        
        dot_product = np.dot(user_vector, product_vector)
        norm_user = np.linalg.norm(user_vector)
        norm_product = np.linalg.norm(product_vector)
        
        score = 0
        if norm_user > 0 and norm_product > 0:
            score = dot_product / (norm_user * norm_product)
        
        match_percentage = int(score * 100)
        
        if match_percentage < 40:
            continue

        recommendations.append(RecommendationItem(
            # ★★★ 2. idをproduct_codeに変更 ★★★
            id=product.product_code,
            name=product.product_name,
            description=product.description,
            image_url=product.image_url,
            location=Location(**supplier_location),
            preferences=PreferenceVector(**product_prefs_dict),
            match_score=match_percentage,
            distance_km=round(distance, 1)
        ))
        
    recommendations.sort(key=lambda item: item.match_score, reverse=True)
    
    return RecommendationResponse(items=recommendations)
@app.post("/favorites")
def add_to_favorites(request: FavoriteRequest, db: Session = Depends(get_db)):
    item_id_str = request.item_id; user_id = request.user_id
    supplier_id_to_save = None; product_id_to_save = None
    try:
        if item_id_str.startswith('s'):
            supplier_id_to_save = int(item_id_str[1:])
        elif item_id_str.startswith('p'):
            product_query = text("SELECT product_id, supplier_id FROM products WHERE product_code = :pcode")
            product_result = db.execute(product_query, {"pcode": item_id_str}).first()
            if product_result:
                product_id_to_save = product_result.product_id
                supplier_id_to_save = product_result.supplier_id
            else: raise HTTPException(status_code=404, detail=f"Product with code {item_id_str} not found")
        else: raise HTTPException(status_code=400, detail="Invalid item_id format")
        
        query = text("INSERT INTO favorites (user_id, supplier_id, product_id, created_at) VALUES (:uid, :sid, :pid, :cat)")
        params = {"uid": user_id, "sid": supplier_id_to_save, "pid": product_id_to_save, "cat": datetime.now()}
        
        db.execute(query, params)
        db.commit()
        return {"message": "Favorite added successfully"}
    except Exception as e:
        db.rollback()
        # ★★★ 2. エラーの詳細を強制的にプリントする ★★★
        print("--- DATABASE ERROR TRACEBACK ---")
        traceback.print_exc()
        print("---------------------------------")
        if "unique constraint" in str(e).lower(): return {"message": "Item is already in favorites"}
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/destinated")
def add_to_destinated(request: DestinatedRequest, db: Session = Depends(get_db)):
    item_id_str = request.item_id; user_id = request.user_id
    supplier_id_to_save = None; product_id_to_save = None
    try:
        if item_id_str.startswith('s'):
            supplier_id_to_save = int(item_id_str[1:])
        elif item_id_str.startswith('p'):
            product_query = text("SELECT product_id, supplier_id FROM products WHERE product_code = :pcode")
            product_result = db.execute(product_query, {"pcode": item_id_str}).first()
            if product_result:
                product_id_to_save = product_result.product_id
                supplier_id_to_save = product_result.supplier_id
            else: raise HTTPException(status_code=404, detail=f"Product with code {item_id_str} not found")
        else: raise HTTPException(status_code=400, detail="Invalid item_id format")
        
        # created_atカラムを追加し、現在時刻をセットする
        query = text("INSERT INTO destinated (user_id, supplier_id, product_id, created_at) VALUES (:uid, :sid, :pid, :cat)")
        params = {"uid": user_id, "sid": supplier_id_to_save, "pid": product_id_to_save, "cat": datetime.now()}
        
        db.execute(query, params)
        db.commit()
        return {"message": "Destinated item added successfully"}
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower(): return {"message": "Item is already in destinated list"}
        raise HTTPException(status_code=500, detail=str(e))

