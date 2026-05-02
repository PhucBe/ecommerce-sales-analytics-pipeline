from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from pydantic import BaseModel, EmailStr, Field


T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int
    returned: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta


class Customer(BaseModel):
    customer_id: str
    customer_name: str
    email: EmailStr
    phone: str | None = None
    city: str
    country: str
    customer_status: str
    created_at: datetime
    updated_at: datetime


class Product(BaseModel):
    product_id: str
    product_name: str
    category: str
    brand: str
    unit_price: Decimal = Field(ge=0)
    cost: Decimal = Field(ge=0)
    product_status: str
    created_at: datetime
    updated_at: datetime


class Order(BaseModel):
    order_id: str
    customer_id: str
    order_date: datetime
    order_status: str
    payment_method: str
    shipping_city: str
    shipping_country: str
    subtotal: Decimal = Field(ge=0)
    discount_amount: Decimal = Field(ge=0)
    shipping_fee: Decimal = Field(ge=0)
    total_amount: Decimal = Field(ge=0)
    created_at: datetime
    updated_at: datetime


class OrderItem(BaseModel):
    order_item_id: str
    order_id: str
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_amount: Decimal = Field(ge=0)
    line_amount: Decimal = Field(ge=0)
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str    