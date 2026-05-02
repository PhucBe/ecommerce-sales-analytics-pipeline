import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from faker import Faker
from app.config import settings


fake = Faker()
Faker.seed(settings.faker_seed)
random.seed(settings.faker_seed)


CATEGORIES = [
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Sports",
    "Books",
    "Beauty",
    "Toys",
    "Grocery",
]

BRANDS = [
    "Nova",
    "UrbanEdge",
    "TechBee",
    "HomePro",
    "FitZone",
    "BookNest",
    "PureSkin",
    "ToyTown",
]

CUSTOMER_STATUSES = ["active", "inactive", "churned"]
PRODUCT_STATUSES = ["active", "inactive", "discontinued"]
ORDER_STATUSES = ["pending", "paid", "shipped", "completed", "cancelled", "refunded"]
PAYMENT_METHODS = ["credit_card", "bank_transfer", "e_wallet", "cod"]


def money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def random_datetime_within_last_year() -> datetime:
    now = datetime.now(timezone.utc)
    days_ago = random.randint(1, 365)
    seconds_ago = random.randint(0, 86400)

    return now - timedelta(days=days_ago, seconds=seconds_ago)


def generate_customers(count: int) -> list[dict]:
    customers = []

    for i in range(1, count + 1):
        created_at = random_datetime_within_last_year()
        updated_at = created_at + timedelta(days=random.randint(0, 90))

        customers.append(
            {
                "customer_id": f"CUST{i:06d}",
                "customer_name": fake.name(),
                "email": fake.unique.email(),
                "phone": fake.phone_number(),
                "city": fake.city(),
                "country": fake.country(),
                "customer_status": random.choices(
                    CUSTOMER_STATUSES,
                    weights=[0.75, 0.15, 0.10],
                    k=1,
                )[0],
                "created_at": created_at,
                "updated_at": updated_at,                
            }
        )

    return customers


def generate_products(count: int) -> list[dict]:
    products = []

    for i in range(1, count + 1):
        category = random.choice(CATEGORIES)
        brand = random.choice(BRANDS)

        cost = money(random.uniform(5, 300))
        markup = random.uniform(1.2, 2.5)
        unit_price = money(float(cost) * markup)

        created_at = random_datetime_within_last_year()
        updated_at = created_at + timedelta(days=random.randint(0, 120))

        products.append(
            {
                "product_id": f"PROD{i:06d}",
                "product_name": f"{brand} {fake.word().title()} {category}",
                "category": category,
                "brand": brand,
                "unit_price": unit_price,
                "cost": cost,
                "product_status": random.choices(
                    PRODUCT_STATUSES,
                    weights=[0.85, 0.10, 0.05],
                    k=1,
                )[0],
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    return products


def generate_orders_and_items(
        order_count: int,
        customers: list[dict],
        products: list[dict],
) -> tuple[list[dict], list[dict]]:
    orders = []
    order_items = []

    for i in range(1, order_count + 1):
        customer = random.choice(customers)
        order_date = random_datetime_within_last_year()

        order_id = f"ORD{i:08d}"
        item_count = random.randint(1, 5)

        selected_products = random.sample(products, k=item_count)

        subtotal = Decimal("0.00")
        item_rows = []

        for line_no, product in enumerate(selected_products, start=1):
            quantity = random.randint(1, 4)
            unit_price = Decimal(str(product["unit_price"]))
            discount_amount = money(random.uniform(0, float(unit_price) * quantity * 0.15))
            line_amount = money((float(unit_price) * quantity) - float(discount_amount))

            subtotal += line_amount

            order_item_id = f"ITEM{i:08d}-{line_no:02d}"

            item_rows.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_amount": discount_amount,
                    "line_amount": line_amount,
                    "created_at": order_date,
                    "updated_at": order_date + timedelta(hours=random.randint(0, 72)),
                }
            )

        order_discount = money(random.uniform(0, float(subtotal) * 0.10))
        shipping_fee = money(random.uniform(0, 15))
        total_amount = money(float(subtotal) - float(order_discount) + float(shipping_fee))

        created_at = order_date
        updated_at = created_at + timedelta(hours=random.randint(0, 96))

        order_status = random.choices(
            ORDER_STATUSES,
            weights=[0.05, 0.15, 0.15, 0.55, 0.05, 0.05],
            k=1,
        )[0]

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date,
                "order_status": order_status,
                "payment_method": random.choice(PAYMENT_METHODS),
                "shipping_city": customer["city"],
                "shipping_country": customer["country"],
                "subtotal": money(float(subtotal)),
                "discount_amount": order_discount,
                "shipping_fee": shipping_fee,
                "total_amount": total_amount,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        order_items.extend(item_rows)

    return orders, order_items


def generate_all_data() -> dict:
    customers = generate_customers(settings.customer_count)
    products = generate_products(settings.product_count)
    orders, order_items = generate_orders_and_items(
        order_count=settings.order_count,
        customers=customers,
        products=products,
    )

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
    }