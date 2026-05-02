from datetime import datetime
from typing import Any
from fastapi import FastAPI, Query
from app.config import settings
from app.generators import generate_all_data
from app.schemas import (
    Customer,
    HealthResponse,
    Order,
    OrderItem,
    PaginatedResponse,
    PaginationMeta,
    Product,
)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Mock E-commerce REST API for Data Engineering Capstone",
)

DATA = generate_all_data()


def paginate(items: list[dict], limit: int, offset: int) -> dict:
    total = len(items)
    sliced = items[offset: offset + limit]

    return {
        "data": sliced,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "returned": len(sliced),
        },
    }


def parse_updated_after(updated_after: str | None) -> datetime | None:
    if updated_after is None:
        return None
    
    return datetime.fromisoformat(updated_after.replace("Z", "+00:00"))


def filter_updated_after(items: list[dict], updated_after: str | None) -> list[dict]:
    parsed_date = parse_updated_after(updated_after)

    if parsed_date is None:
        return items
    
    return [
        item
        for item in items
        if item["updated_at"] >= parsed_date
    ]


@app.get("/health", response_model=HealthResponse)
def health_check() -> dict:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/customers", response_model=PaginatedResponse[Customer])
def get_customers(
    limit: int = Query(default=settings.default_limit, ge=1, le=settings.max_limit),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    city: str | None = Query(default=None),
    country: str | None = Query(default=None),
    updated_after: str | None = Query(default=None),
) -> dict:
    items = DATA["customers"]

    if status:
        items = [x for x in items if x["customer_status"] == status]

    if city:
        items = [x for x in items if x["city"].lower() == city.lower()]

    if country:
        items = [x for x in items if x["country"].lower() == country.lower()]

    items = filter_updated_after(items, updated_after)

    return paginate(items, limit, offset)


@app.get("/products", response_model=PaginatedResponse[Product])
def get_products(
    limit: int = Query(default=settings.default_limit, ge=1, le=settings.max_limit),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    status: str | None = Query(default=None),
    updated_after: str | None = Query(default=None),
) -> dict:
    items = DATA["products"]

    if category:
        items = [x for x in items if x["category"].lower() == category.lower()]

    if brand:
        items = [x for x in items if x["brand"].lower() == brand.lower()]

    if status:
        items = [x for x in items if x["product_status"] == status]

    items = filter_updated_after(items, updated_after)

    return paginate(items, limit, offset)


@app.get("/orders", response_model=PaginatedResponse[Order])
def get_orders(
    limit: int = Query(default=settings.default_limit, ge=1, le=settings.max_limit),
    offset: int = Query(default=0, ge=0),
    customer_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    payment_method: str | None = Query(default=None),
    updated_after: str | None = Query(default=None),
) -> dict:
    items = DATA["orders"]

    if customer_id:
        items = [x for x in items if x["customer_id"] == customer_id]

    if status:
        items = [x for x in items if x["order_status"] == status]

    if payment_method:
        items = [x for x in items if x["payment_method"] == payment_method]

    items = filter_updated_after(items, updated_after)

    return paginate(items, limit, offset)


@app.get("/order-items", response_model=PaginatedResponse[OrderItem])
def get_order_items(
    limit: int = Query(default=settings.default_limit, ge=1, le=settings.max_limit),
    offset: int = Query(default=0, ge=0),
    order_id: str | None = Query(default=None),
    product_id: str | None = Query(default=None),
    updated_after: str | None = Query(default=None),
) -> dict:
    items = DATA["order_items"]

    if order_id:
        items = [x for x in items if x["order_id"] == order_id]

    if product_id:
        items = [x for x in items if x["product_id"] == product_id]

    items = filter_updated_after(items, updated_after)

    return paginate(items, limit, offset)