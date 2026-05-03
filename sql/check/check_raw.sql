WITH checks AS (
    -- 1. ROW COUNT CHECKS
    SELECT
        'raw_customers_row_count_gt_0' AS check_name,
        'FAIL' AS severity,
        CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
        CONCAT('row_count=', COUNT(*)) AS details
    FROM raw_layer.raw_customers

    UNION ALL

    SELECT
        'raw_products_row_count_gt_0' AS check_name,
        'FAIL' AS severity,
        CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
        CONCAT('row_count=', COUNT(*)) AS details
    FROM raw_layer.raw_products

    UNION ALL

    SELECT
        'raw_orders_row_count_gt_0' AS check_name,
        'FAIL' AS severity,
        CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
        CONCAT('row_count=', COUNT(*)) AS details
    FROM raw_layer.raw_orders

    UNION ALL

    SELECT
        'raw_order_items_row_count_gt_0' AS check_name,
        'FAIL' AS severity,
        CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS violation_count,
        CONCAT('row_count=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items

    -- 2. KEY NOT NULL CHECKS
    UNION ALL

    SELECT
        'raw_customers_customer_id_not_null' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('null_or_blank_customer_id=', COUNT(*)) AS details
    FROM raw_layer.raw_customers
    WHERE customer_id IS NULL
       OR BTRIM(customer_id) = ''

    UNION ALL

    SELECT
        'raw_products_product_id_not_null' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('null_or_blank_product_id=', COUNT(*)) AS details
    FROM raw_layer.raw_products
    WHERE product_id IS NULL
       OR BTRIM(product_id) = ''

    UNION ALL

    SELECT
        'raw_orders_keys_not_null' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('orders_with_null_or_blank_key=', COUNT(*)) AS details
    FROM raw_layer.raw_orders
    WHERE order_id IS NULL
       OR BTRIM(order_id) = ''
       OR customer_id IS NULL
       OR BTRIM(customer_id) = ''

    UNION ALL

    SELECT
        'raw_order_items_keys_not_null' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('order_items_with_null_or_blank_key=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items
    WHERE order_item_id IS NULL
       OR BTRIM(order_item_id) = ''
       OR order_id IS NULL
       OR BTRIM(order_id) = ''
       OR product_id IS NULL
       OR BTRIM(product_id) = ''

    -- 3. DATE CHECKS
    UNION ALL

    SELECT
        'raw_orders_order_date_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_order_date_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_orders
    WHERE order_date IS NULL
       OR order_date < TIMESTAMPTZ '2020-01-01'
       OR order_date > NOW() + INTERVAL '1 day'

    -- 4. NUMERIC CHECKS
    UNION ALL

    SELECT
        'raw_products_price_and_cost_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_product_price_or_cost_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_products
    WHERE unit_price IS NULL
       OR unit_price < 0
       OR cost IS NULL
       OR cost < 0

    UNION ALL

    SELECT
        'raw_order_items_quantity_positive' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_quantity_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items
    WHERE quantity IS NULL
       OR quantity <= 0

    UNION ALL

    SELECT
        'raw_order_items_price_and_discount_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_unit_price_or_discount_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items
    WHERE unit_price IS NULL
       OR unit_price < 0
       OR discount_amount IS NULL
       OR discount_amount < 0

    UNION ALL

    SELECT
        'raw_order_items_line_amount_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_line_amount_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items
    WHERE quantity IS NULL
       OR unit_price IS NULL
       OR discount_amount IS NULL
       OR line_amount IS NULL
       OR line_amount < 0
       OR ABS(line_amount - ((quantity * unit_price) - discount_amount)) > 0.01

    UNION ALL

    SELECT
        'raw_orders_total_amount_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_total_amount_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_orders
    WHERE subtotal IS NULL
       OR discount_amount IS NULL
       OR shipping_fee IS NULL
       OR total_amount IS NULL
       OR subtotal < 0
       OR discount_amount < 0
       OR shipping_fee < 0
       OR total_amount < 0
       OR ABS(total_amount - (subtotal - discount_amount + shipping_fee)) > 0.01

    -- 5. RELATIONSHIP CHECKS
    UNION ALL

    SELECT
        'raw_orders_customer_id_exists_in_customers' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('orders_missing_customer=', COUNT(*)) AS details
    FROM raw_layer.raw_orders o
    LEFT JOIN raw_layer.raw_customers c
        ON o.customer_id = c.customer_id
    WHERE o.customer_id IS NOT NULL
      AND c.customer_id IS NULL

    UNION ALL

    SELECT
        'raw_order_items_order_id_exists_in_orders' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('order_items_missing_order=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items oi
    LEFT JOIN raw_layer.raw_orders o
        ON oi.order_id = o.order_id
    WHERE oi.order_id IS NOT NULL
      AND o.order_id IS NULL

    UNION ALL

    SELECT
        'raw_order_items_product_id_exists_in_products' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('order_items_missing_product=', COUNT(*)) AS details
    FROM raw_layer.raw_order_items oi
    LEFT JOIN raw_layer.raw_products p
        ON oi.product_id = p.product_id
    WHERE oi.product_id IS NOT NULL
      AND p.product_id IS NULL

    -- 6. STATUS CHECKS
    UNION ALL

    SELECT
        'raw_customers_status_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_customer_status_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_customers
    WHERE customer_status IS NULL
       OR customer_status NOT IN ('active', 'inactive', 'churned')

    UNION ALL

    SELECT
        'raw_products_status_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_product_status_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_products
    WHERE product_status IS NULL
       OR product_status NOT IN ('active', 'inactive', 'discontinued')

    UNION ALL

    SELECT
        'raw_orders_status_valid' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('invalid_order_status_rows=', COUNT(*)) AS details
    FROM raw_layer.raw_orders
    WHERE order_status IS NULL
       OR order_status NOT IN ('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded')

    -- 7. TECHNICAL METADATA CHECKS
    UNION ALL

    SELECT
        'raw_technical_metadata_not_null' AS check_name,
        'FAIL' AS severity,
        COUNT(*) AS violation_count,
        CONCAT('rows_missing_technical_metadata=', COUNT(*)) AS details
    FROM (
        SELECT ingested_at, batch_id, source_system, raw_payload FROM raw_layer.raw_customers
        UNION ALL
        SELECT ingested_at, batch_id, source_system, raw_payload FROM raw_layer.raw_products
        UNION ALL
        SELECT ingested_at, batch_id, source_system, raw_payload FROM raw_layer.raw_orders
        UNION ALL
        SELECT ingested_at, batch_id, source_system, raw_payload FROM raw_layer.raw_order_items
    ) t
    WHERE ingested_at IS NULL
       OR batch_id IS NULL
       OR source_system IS NULL
       OR raw_payload IS NULL

    -- 8. DUPLLICATE CHECKS - WARNING ONLY
    UNION ALL

    SELECT
        'raw_customers_duplicate_customer_id' AS check_name,
        'WARN' AS severity,
        COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
        CONCAT('duplicate_customer_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
    FROM (
        SELECT COUNT(*) - 1 AS duplicate_count
        FROM raw_layer.raw_customers
        WHERE customer_id IS NOT NULL
          AND BTRIM(customer_id) <> ''
        GROUP BY customer_id
        HAVING COUNT(*) > 1
    ) d

    UNION ALL

    SELECT
        'raw_products_duplicate_product_id' AS check_name,
        'WARN' AS severity,
        COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
        CONCAT('duplicate_product_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
    FROM (
        SELECT COUNT(*) - 1 AS duplicate_count
        FROM raw_layer.raw_products
        WHERE product_id IS NOT NULL
          AND BTRIM(product_id) <> ''
        GROUP BY product_id
        HAVING COUNT(*) > 1
    ) d

    UNION ALL

    SELECT
        'raw_orders_duplicate_order_id' AS check_name,
        'WARN' AS severity,
        COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
        CONCAT('duplicate_order_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
    FROM (
        SELECT COUNT(*) - 1 AS duplicate_count
        FROM raw_layer.raw_orders
        WHERE order_id IS NOT NULL
          AND BTRIM(order_id) <> ''
        GROUP BY order_id
        HAVING COUNT(*) > 1
    ) d

    UNION ALL

    SELECT
        'raw_order_items_duplicate_order_item_id' AS check_name,
        'WARN' AS severity,
        COALESCE(SUM(duplicate_count), 0)::BIGINT AS violation_count,
        CONCAT('duplicate_order_item_id_rows=', COALESCE(SUM(duplicate_count), 0)) AS details
    FROM (
        SELECT COUNT(*) - 1 AS duplicate_count
        FROM raw_layer.raw_order_items
        WHERE order_item_id IS NOT NULL
          AND BTRIM(order_item_id) <> ''
        GROUP BY order_item_id
        HAVING COUNT(*) > 1
    ) d
)
SELECT
    check_name,
    severity,
    violation_count,
    CASE
        WHEN violation_count = 0 THEN 'PASS'
        WHEN severity = 'WARN' THEN 'WARN'
        ELSE 'FAIL'
    END AS status,
    details
FROM checks
ORDER BY
    CASE
        WHEN violation_count > 0 AND severity = 'FAIL' THEN 1
        WHEN violation_count > 0 AND severity = 'WARN' THEN 2
        ELSE 3
    END,
    check_name;