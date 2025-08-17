import os
import json
import math
import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

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
    supplier_query = text("SELECT supplier_id, name, description, image_url, heritage_soul, modern_heirloom, folk_heart, fresh_folk, masterpiece, innovative_classic, craft_sense, smart_craft, signature_mood, iconic_style, local_trend, playful_pop, design_master, global_trend, smart_local, smart_pick FROM suppliers ORDER BY RANDOM() LIMIT 3")
    suppliers_result = db.execute(supplier_query).fetchall()
    product_query = text("SELECT product_code, name, description, image_url, heritage_soul, modern_heirloom, folk_heart, fresh_folk, masterpiece, innovative_classic, craft_sense, smart_craft, signature_mood, iconic_style, local_trend, playful_pop, design_master, global_trend, smart_local, smart_pick FROM products ORDER BY RANDOM() LIMIT 3")
    products_result = db.execute(product_query).fetchall()
    suppliers = [Item(id=f"s{row.supplier_id}", name=row.name, description=row.description, image_url=row.image_url, preferences=PreferenceVector(**row._mapping)) for row in suppliers_result]
    products = [Item(id=row.product_code, name=row.name, description=row.description, image_url=row.image_url, preferences=PreferenceVector(**row._mapping)) for row in products_result]
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
    user = db.execute(text("SELECT * FROM users WHERE user_id = :uid"), {"uid": user_id}).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user_prefs_dict = {key: getattr(user, key, 0) for key in PreferenceVector.model_fields.keys()}
    user_vector = np.array(list(user_prefs_dict.values()))
    suppliers = db.execute(text("SELECT * FROM suppliers")).fetchall()
    recommendations = []
    for supplier in suppliers:
        supplier_location = json.loads(supplier.location) if isinstance(supplier.location, str) else supplier.location
        if not supplier_location: continue
        distance = haversine_distance(latitude, longitude, supplier_location['lat'], supplier_location['lng'])
        if distance > 10: continue
        supplier_prefs_dict = {key: getattr(supplier, key, 0) for key in PreferenceVector.model_fields.keys()}
        supplier_vector = np.array(list(supplier_prefs_dict.values()))
        dot_product = np.dot(user_vector, supplier_vector)
        norm_user = np.linalg.norm(user_vector)
        norm_supplier = np.linalg.norm(supplier_vector)
        score = 0 if norm_user == 0 or norm_supplier == 0 else dot_product / (norm_user * norm_supplier)
        match_percentage = int(score * 100)
        if match_percentage < 40: continue
        recommendations.append(RecommendationItem(id=f"s{supplier.supplier_id}", name=supplier.name, description=supplier.description, image_url=supplier.image_url, location=Location(**supplier_location), preferences=PreferenceVector(**supplier._mapping), match_score=match_percentage, distance_km=round(distance, 1)))
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
        query = text("INSERT INTO favorites (user_id, supplier_id, product_id) VALUES (:uid, :sid, :pid)")
        params = {"uid": user_id, "sid": supplier_id_to_save, "pid": product_id_to_save}
        db.execute(query, params)
        db.commit()
        return {"message": "Favorite added successfully"}
    except Exception as e:
        db.rollback()
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
        query = text("INSERT INTO destinated (user_id, supplier_id, product_id) VALUES (:uid, :sid, :pid)")
        params = {"uid": user_id, "sid": supplier_id_to_save, "pid": product_id_to_save}
        db.execute(query, params)
        db.commit()
        return {"message": "Destinated item added successfully"}
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower(): return {"message": "Item is already in destinated list"}
        raise HTTPException(status_code=500, detail=str(e))
