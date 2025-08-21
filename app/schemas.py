from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional,TypeVar,Generic
from datetime import datetime
import json
from app.enums import Role, AccountStatus

T=TypeVar("T")

class OurBaseModel(BaseModel):
    class Config:
        from_attributes = True

class OurBaseModelOut(OurBaseModel):
    message: Optional[str] = None
    status: Optional[int] = None

class PagedResponse(OurBaseModelOut,Generic[T]):
    data:List[T]=[]
    page_number: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    total_records: Optional[int] = None

class BaseFilter(OurBaseModel):
    name_substr: Optional[str]= None
    page_size: Optional[int] = 10
    page_number: Optional[int] = 1

class UserBase(OurBaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Role = Role.Buyer

class UserUpdate(BaseModel):
    first_name: Optional[str]=None
    last_name: Optional[str]=None
    email: Optional[EmailStr]=None
    role: Optional[Role]=None
    status: Optional[AccountStatus]=None

class UserRead(UserBase):
    id: int
    role: Role
    status: AccountStatus
    sessions: Optional[List[SessionBase]] = []

class CategoryBase(OurBaseModel):
    name: str
    description: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    products: Optional[List[ProductRead]] = []
    image_link:str

class CategoryUpdate(OurBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int
    image_link: str

class ProductBase(OurBaseModel):
    name: str
    unit_price: Decimal
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    unit_price: Optional[Decimal] = None
    category_id: Optional[int] = None

class ProductRead(ProductBase):
    id: int

class ProductOut(ProductBase):
    id: int
    category: CategoryOut  

class TokenData(OurBaseModel):
    id: int = None

class OrderItemBase(OurBaseModel):
    product_id: int
    quantity: Decimal
    unit_price: Decimal

class OrderItemRead(OrderItemBase):
    id: int
    product: ProductOut

class OrderBase(OurBaseModel):
    buyer_id: int
    buyer_phone: int
    buyer_address: str
    items: List[OrderItemBase]

class OrderRead(OrderBase):
    id: int
    status: str
    created_on: datetime
    items: List[OrderItemRead]

class MailData(OurBaseModel):
    emails: List[EmailStr]
    body: Dict[str, Any]
    template: str
    subject: str

class AccessToken(OurBaseModelOut):
    token_type: str
    access_token: str

class ForgetPassword(OurBaseModel):
    email: EmailStr

class ConfirmData(OurBaseModel):
    confirmation_code:str

class ResetPassword(OurBaseModel):
    confirmation_code:str
    password:str
    confirm_password:str

class Location(OurBaseModel):
    country: str | None = None
    region: str | None = None
    city: str | None = None
    lat: float | None = None
    lon: float | None = None

class SessionBase(OurBaseModel):
    id:int
    ip_address: str | None = None
    user_agent: str | None = None
    location: Location | None = None
    last_activity_at: datetime | None = None
    created_at: datetime | None = None
    is_active: bool = True
    user_id: int

    class Config:
        @staticmethod
        def json_schema_extra(obj):
            if isinstance(obj, dict) and "location" in obj and obj["location"]:
                obj["location"] = json.loads(obj["location"])

