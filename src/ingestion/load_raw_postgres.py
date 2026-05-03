from __future__ import annotations
from datetime import datetime
from typing import Any
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json, execute_values


DATASET_TABLE_MAP = {
    "customers": "raw_customers",
    "products": "raw_products",
    "orders": "raw_orders",
    "order_items": "raw_order_items",
}

DATASET_COLUMNS = {
    "customers": [
        "customer_id",
        "customer_name",
        "email",
        "phone",
        "city",
        "country",
        "customer_status",
        "created_at",
        "updated_at",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "brand",
        "unit_price",
        "cost",
        "product_status",
        "created_at",
        "updated_at",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_date",
        "order_status",
        "payment_method",
        "shipping_city",
        "shipping_country",
        "subtotal",
        "discount_amount",
        "shipping_fee",
        "total_amount",
        "created_at",
        "updated_at",
    ],
    "order_items": [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_amount",
        "line_amount",
        "created_at",
        "updated_at",
    ],
}

TRUNCATE_TABLE_ORDER = [
    "raw_order_items",
    "raw_orders",
    "raw_products",
    "raw_customers",
]


def get_postgres_connection(config: dict[str, Any]):
    postgres_config = config["postgres"]

    return psycopg2.connect(
        host=postgres_config["host"],
        port=postgres_config["port"],
        dbname=postgres_config["database"],
        user=postgres_config["user"],
        password=postgres_config["password"],
    )


def truncate_raw_tables(
        connection,
        schema_name: str,
        logger: logging.Logger,
) -> None:
    table_identifiers = [
        sql.SQL("{}.{}").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
        )
        for table_name in TRUNCATE_TABLE_ORDER
    ]

    truncate_sql = sql.SQL("TRUNCATE TABLE {}").format(
        sql.SQL(", ").join(table_identifiers)
    )

    with connection.cursor() as cursor:
        logger.info("Truncating raw tables in schema=%s", schema_name)
        cursor.execute(truncate_sql)

    logger.info("Raw tables truncated successfully.")


def insert_dataset_records(
        connection,
        schema_name: str,
        dataset_name: str,
        records: list[dict[str, Any]],
        batch_id: str,
        source_system: str,
        ingested_at: datetime,
        logger: logging.Logger,
) -> int:
    if dataset_name not in DATASET_TABLE_MAP:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    if dataset_name not in DATASET_COLUMNS:
        raise ValueError(f"Missing column mapping for dataset_name: {dataset_name}")

    if not records:
        logger.warning("No records to insert for dataset=%s", dataset_name)
        return 0

    table_name = DATASET_TABLE_MAP[dataset_name]
    business_columns = DATASET_COLUMNS[dataset_name]

    metadata_columns = [
        "ingested_at",
        "batch_id",
        "source_system",
        "raw_payload",
    ]

    insert_columns = business_columns + metadata_columns

    rows = []

    for record in records:
        row = [record.get(column_name) for column_name in business_columns]
        row.extend(
            [
                ingested_at,
                batch_id,
                source_system,
                Json(record),
            ]
        )
        rows.append(tuple(row))

    insert_sql = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(column_name) for column_name in insert_columns),
    )

    with connection.cursor() as cursor:
        execute_values(
            cursor,
            insert_sql.as_string(cursor),
            rows,
            page_size=1000,
        )

    logger.info(
        "Inserted dataset=%s table=%s.%s row_count=%s batch_id=%s",
        dataset_name,
        schema_name,
        table_name,
        len(rows),
        batch_id,
    )

    return len(rows)


def get_latest_updated_at(
        connection,
        schema_name: str,
        dataset_name: str,
) -> datetime | None:
    if dataset_name not in DATASET_TABLE_MAP:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    table_name = DATASET_TABLE_MAP[dataset_name]

    query = sql.SQL("SELECT MAX(updated_at) FROM {}.{}").format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    if not result:
        return None

    return result[0]