from __future__ import annotations
import argparse
import sys
from typing import Any
from src.common.config import load_app_config
from src.common.logger import get_logger
from src.ingestion.load_raw_postgres import get_postgres_connection


def table_name(schema_name: str, table: str) -> str:
    return f'"{schema_name}"."{table}"'


def build_checks(schema_name: str) -> list[dict[str, str]]:
    raw_customers = table_name(schema_name, "raw_customers")
    raw_products = table_name(schema_name, "raw_products")
    raw_orders = table_name(schema_name, "raw_orders")
    raw_order_items = table_name(schema_name, "raw_order_items")

    return [
        # 1. ROW COUNT CHECKS
        {
            "name": "raw_customers_row_count_gt_0",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
                    CONCAT('row_count=', COUNT(*)) AS details
                FROM {raw_customers}
            """,
        },
        {
            "name": "raw_products_row_count_gt_0",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
                    CONCAT('row_count=', COUNT(*)) AS details
                FROM {raw_products}
            """,
        },
        {
            "name": "raw_orders_row_count_gt_0",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
                    CONCAT('row_count=', COUNT(*)) AS details
                FROM {raw_orders}
            """,
        },
        {
            "name": "raw_order_items_row_count_gt_0",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
                    CONCAT('row_count=', COUNT(*)) AS details
                FROM {raw_order_items}
            """,
        },

        # 2. KEY NOT NULL CHECKS
        {
            "name": "raw_customers_customer_id_not_null",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('null_or_blank_customer_id=', COUNT(*)) AS details
                FROM {raw_customers}
                WHERE customer_id IS NULL
                   OR BTRIM(customer_id) = ''
            """,
        },
        {
            "name": "raw_products_product_id_not_null",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('null_or_blank_product_id=', COUNT(*)) AS details
                FROM {raw_products}
                WHERE product_id IS NULL
                   OR BTRIM(product_id) = ''
            """,
        },
        {
            "name": "raw_orders_keys_not_null",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('orders_with_null_or_blank_key=', COUNT(*)) AS details
                FROM {raw_orders}
                WHERE order_id IS NULL
                   OR BTRIM(order_id) = ''
                   OR customer_id IS NULL
                   OR BTRIM(customer_id) = ''
            """,
        },
        {
            "name": "raw_order_items_keys_not_null",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('order_items_with_null_or_blank_key=', COUNT(*)) AS details
                FROM {raw_order_items}
                WHERE order_item_id IS NULL
                   OR BTRIM(order_item_id) = ''
                   OR order_id IS NULL
                   OR BTRIM(order_id) = ''
                   OR product_id IS NULL
                   OR BTRIM(product_id) = ''
            """,
        },

        # 3. DATE CHECKS
        {
            "name": "raw_orders_order_date_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_order_date_rows=', COUNT(*)) AS details
                FROM {raw_orders}
                WHERE order_date IS NULL
                   OR order_date < TIMESTAMPTZ '2020-01-01'
                   OR order_date > NOW() + INTERVAL '1 day'
            """,
        },

        # 4. NUMERIC CHECKS
        {
            "name": "raw_products_price_and_cost_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_product_price_or_cost_rows=', COUNT(*)) AS details
                FROM {raw_products}
                WHERE unit_price IS NULL
                   OR unit_price < 0
                   OR cost IS NULL
                   OR cost < 0
            """,
        },
        {
            "name": "raw_order_items_quantity_positive",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_quantity_rows=', COUNT(*)) AS details
                FROM {raw_order_items}
                WHERE quantity IS NULL
                   OR quantity <= 0
            """,
        },
        {
            "name": "raw_order_items_price_and_discount_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_unit_price_or_discount_rows=', COUNT(*)) AS details
                FROM {raw_order_items}
                WHERE unit_price IS NULL
                   OR unit_price < 0
                   OR discount_amount IS NULL
                   OR discount_amount < 0
            """,
        },
        {
            "name": "raw_order_items_line_amount_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_line_amount_rows=', COUNT(*)) AS details
                FROM {raw_order_items}
                WHERE quantity IS NULL
                   OR unit_price IS NULL
                   OR discount_amount IS NULL
                   OR line_amount IS NULL
                   OR line_amount < 0
                   OR ABS(line_amount - ((quantity * unit_price) - discount_amount)) > 0.01
            """,
        },
        {
            "name": "raw_orders_total_amount_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_total_amount_rows=', COUNT(*)) AS details
                FROM {raw_orders}
                WHERE subtotal IS NULL
                   OR discount_amount IS NULL
                   OR shipping_fee IS NULL
                   OR total_amount IS NULL
                   OR subtotal < 0
                   OR discount_amount < 0
                   OR shipping_fee < 0
                   OR total_amount < 0
                   OR ABS(total_amount - (subtotal - discount_amount + shipping_fee)) > 0.01
            """,
        },

        # 5. RELATIONSHIP CHECKS
        {
            "name": "raw_orders_customer_id_exists_in_customers",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('orders_missing_customer=', COUNT(*)) AS details
                FROM {raw_orders} o
                LEFT JOIN {raw_customers} c
                    ON o.customer_id = c.customer_id
                WHERE o.customer_id IS NOT NULL
                  AND c.customer_id IS NULL
            """,
        },
        {
            "name": "raw_order_items_order_id_exists_in_orders",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('order_items_missing_order=', COUNT(*)) AS details
                FROM {raw_order_items} oi
                LEFT JOIN {raw_orders} o
                    ON oi.order_id = o.order_id
                WHERE oi.order_id IS NOT NULL
                  AND o.order_id IS NULL
            """,
        },
        {
            "name": "raw_order_items_product_id_exists_in_products",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('order_items_missing_product=', COUNT(*)) AS details
                FROM {raw_order_items} oi
                LEFT JOIN {raw_products} p
                    ON oi.product_id = p.product_id
                WHERE oi.product_id IS NOT NULL
                  AND p.product_id IS NULL
            """,
        },

        # 6. STATUS CHECKS
        {
            "name": "raw_customers_status_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_customer_status_rows=', COUNT(*)) AS details
                FROM {raw_customers}
                WHERE customer_status IS NULL
                   OR customer_status NOT IN ('active', 'inactive', 'churned')
            """,
        },
        {
            "name": "raw_products_status_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_product_status_rows=', COUNT(*)) AS details
                FROM {raw_products}
                WHERE product_status IS NULL
                   OR product_status NOT IN ('active', 'inactive', 'discontinued')
            """,
        },
        {
            "name": "raw_orders_status_valid",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('invalid_order_status_rows=', COUNT(*)) AS details
                FROM {raw_orders}
                WHERE order_status IS NULL
                   OR order_status NOT IN (
                        'pending',
                        'paid',
                        'shipped',
                        'completed',
                        'cancelled',
                        'refunded'
                   )
            """,
        },

        # 7. TECHNICAL METADATA CHECKS
        {
            "name": "raw_technical_metadata_not_null",
            "severity": "FAIL",
            "sql": f"""
                SELECT
                    COUNT(*) AS violation_count,
                    CONCAT('rows_missing_technical_metadata=', COUNT(*)) AS details
                FROM (
                    SELECT ingested_at, batch_id, source_system, raw_payload FROM {raw_customers}
                    UNION ALL
                    SELECT ingested_at, batch_id, source_system, raw_payload FROM {raw_products}
                    UNION ALL
                    SELECT ingested_at, batch_id, source_system, raw_payload FROM {raw_orders}
                    UNION ALL
                    SELECT ingested_at, batch_id, source_system, raw_payload FROM {raw_order_items}
                ) t
                WHERE ingested_at IS NULL
                   OR batch_id IS NULL
                   OR source_system IS NULL
                   OR raw_payload IS NULL
            """,
        },

        # 8. DUPLICATE CHECKS - WARNING ONLY
        {
            "name": "raw_customers_duplicate_customer_id",
            "severity": "WARN",
            "sql": f"""
                SELECT
                    COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
                    CONCAT('duplicate_customer_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
                FROM (
                    SELECT COUNT(*) - 1 AS duplicate_count
                    FROM {raw_customers}
                    WHERE customer_id IS NOT NULL
                      AND BTRIM(customer_id) <> ''
                    GROUP BY customer_id
                    HAVING COUNT(*) > 1
                ) d
            """,
        },
        {
            "name": "raw_products_duplicate_product_id",
            "severity": "WARN",
            "sql": f"""
                SELECT
                    COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
                    CONCAT('duplicate_product_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
                FROM (
                    SELECT COUNT(*) - 1 AS duplicate_count
                    FROM {raw_products}
                    WHERE product_id IS NOT NULL
                      AND BTRIM(product_id) <> ''
                    GROUP BY product_id
                    HAVING COUNT(*) > 1
                ) d
            """,
        },
        {
            "name": "raw_orders_duplicate_order_id",
            "severity": "WARN",
            "sql": f"""
                SELECT
                    COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
                    CONCAT('duplicate_order_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
                FROM (
                    SELECT COUNT(*) - 1 AS duplicate_count
                    FROM {raw_orders}
                    WHERE order_id IS NOT NULL
                      AND BTRIM(order_id) <> ''
                    GROUP BY order_id
                    HAVING COUNT(*) > 1
                ) d
            """,
        },
        {
            "name": "raw_order_items_duplicate_order_item_id",
            "severity": "WARN",
            "sql": f"""
                SELECT
                    COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
                    CONCAT('duplicate_order_item_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
                FROM (
                    SELECT COUNT(*) - 1 AS duplicate_count
                    FROM {raw_order_items}
                    WHERE order_item_id IS NOT NULL
                      AND BTRIM(order_item_id) <> ''
                    GROUP BY order_item_id
                    HAVING COUNT(*) > 1
                ) d
            """,
        },
    ]


def run_checks(connection: Any, checks: list[dict[str, str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    with connection.cursor() as cursor:
        for check in checks:
            cursor.execute(check["sql"])
            row = cursor.fetchone()

            if row is None:
                raise RuntimeError(f"Check returned no result: {check['name']}")

            violation_count = int(row[0])
            details = str(row[1])

            if violation_count == 0:
                status = "PASS"
            elif check["severity"] == "WARN":
                status = "WARN"
            else:
                status = "FAIL"

            results.append(
                {
                    "check_name": check["name"],
                    "severity": check["severity"],
                    "violation_count": violation_count,
                    "status": status,
                    "details": details,
                }
            )

    return results


def print_results(results: list[dict[str, Any]]) -> None:
    headers = [
        "status",
        "severity",
        "violation_count",
        "check_name",
        "details",
    ]

    rows = [
        [
            result["status"],
            result["severity"],
            str(result["violation_count"]),
            result["check_name"],
            result["details"],
        ]
        for result in results
    ]

    column_widths = []

    for index, header in enumerate(headers):
        max_width = len(header)

        for row in rows:
            max_width = max(max_width, len(row[index]))

        column_widths.append(max_width)

    header_line = " | ".join(
        header.ljust(column_widths[index])
        for index, header in enumerate(headers)
    )

    separator_line = "-+-".join(
        "-" * column_width
        for column_width in column_widths
    )

    print(header_line)
    print(separator_line)

    for row in rows:
        print(
            " | ".join(
                row[index].ljust(column_widths[index])
                for index in range(len(headers))
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate PostgreSQL raw layer for Ecommerce Sales Analytics"
    )

    parser.add_argument(
        "--env",
        default=None,
        help="Config environment name. Default reads APP_ENV or config/settings.yml",
    )

    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Treat WARN checks as pipeline failure",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = load_app_config(env_name=args.env)

    logger = get_logger(
        name="validate_raw",
        log_dir=config["paths"]["log_dir"],
    )

    schema_name = config["postgres"]["schema_raw"]

    logger.info("=" * 80)
    logger.info("START RAW VALIDATION")
    logger.info("schema=%s", schema_name)
    logger.info("=" * 80)

    checks = build_checks(schema_name=schema_name)
    connection = get_postgres_connection(config)

    try:
        results = run_checks(
            connection=connection,
            checks=checks,
        )

    finally:
        connection.close()

    results = sorted(
        results,
        key=lambda item: (
            0 if item["status"] == "FAIL" else 1 if item["status"] == "WARN" else 2,
            item["check_name"],
        ),
    )

    print_results(results)

    fail_count = sum(
        1
        for result in results
        if result["status"] == "FAIL"
    )

    warn_count = sum(
        1
        for result in results
        if result["status"] == "WARN"
    )

    if fail_count > 0:
        logger.error(
            "RAW VALIDATION FAILED. fail_count=%s warn_count=%s",
            fail_count,
            warn_count,
        )
        sys.exit(1)

    if args.fail_on_warn and warn_count > 0:
        logger.error(
            "RAW VALIDATION FAILED BECAUSE --fail-on-warn IS ENABLED. warn_count=%s",
            warn_count,
        )
        sys.exit(2)

    logger.info(
        "RAW VALIDATION PASSED. fail_count=%s warn_count=%s",
        fail_count,
        warn_count,
    )


if __name__ == "__main__":
    main()