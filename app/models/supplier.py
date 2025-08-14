from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from sqlalchemy.sql import func
from app.database import Base
from dataclasses import dataclass
from typing import Dict, Optional, List
import json

@dataclass
class Location:
    lat: float
    lng: float
    
    def to_dict(self) -> Dict[str, float]:
        return {"lat": self.lat, "lng": self.lng}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Location':
        return cls(lat=data['lat'], lng=data['lng'])

class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    hours = Column(String(255))
    website = Column(String(255))
    location = Column(JSON, nullable=False)
    city = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    categories = Column(JSON, nullable=True)  # カテゴリーカラムを追加
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Locationオブジェクトとして扱うためのプロパティ
    @property
    def location_obj(self) -> Optional[Location]:
        if self.location:
            return Location.from_dict(self.location)
        return None
    
    @location_obj.setter
    def location_obj(self, value: Optional[Location]):
        if value:
            self.location = value.to_dict()
        else:
            self.location = None
    
    # カテゴリーリストとして扱うためのプロパティ
    @property
    def categories_list(self) -> List[str]:
        """カテゴリーをリストとして取得"""
        if self.categories:
            return self.categories if isinstance(self.categories, list) else []
        return []
    
    @categories_list.setter
    def categories_list(self, value: List[str]):
        """カテゴリーをリストとして設定"""
        self.categories = value if value else []