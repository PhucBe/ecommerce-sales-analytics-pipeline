CREATE TABLE IF NOT EXISTS raw_layer.raw_customers (
    customer_id VARCHAR(50),
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    customer_status VARCHAR(30),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,

    -- Technical metadata
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    batch_id VARCHAR(100),
    source_system VARCHAR(50) NOT NULL DEFAULT 'mock_api',
    raw_payload JSONB
);


CREATE TABLE IF NOT EXISTS raw_layer.raw_products (
    product_id VARCHAR(50),
    product_name TEXT,
    category TEXT,
    brand TEXT,
    unit_price NUMERIC(12, 2),
    cost NUMERIC(12, 2),
    product_status VARCHAR(30),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,

    -- Technical metadata
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    batch_id VARCHAR(100),
    source_system VARCHAR(50) NOT NULL DEFAULT 'mock_api',
    raw_payload JSONB
);


CREATE TABLE IF NOT EXISTS raw_layer.raw_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    order_date TIMESTAMPTZ,
    order_status VARCHAR(30),
    payment_method VARCHAR(50),
    shipping_city TEXT,
    shipping_country TEXT,
    subtotal NUMERIC(12, 2),
    discount_amount NUMERIC(12, 2),
    shipping_fee NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,

    -- Technical metadata
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    batch_id VARCHAR(100),
    source_system VARCHAR(50) NOT NULL DEFAULT 'mock_api',
    raw_payload JSONB
);


CREATE TABLE IF NOT EXISTS raw_layer.raw_order_items (
    order_item_id VARCHAR(80),
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INTEGER,
    unit_price NUMERIC(12, 2),
    discount_amount NUMERIC(12, 2),
    line_amount NUMERIC(12, 2),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,

    -- Technical metadata
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    batch_id VARCHAR(100),
    source_system VARCHAR(50) NOT NULL DEFAULT 'mock_api',
    raw_payload JSONB
);


-- Indexes for common lookup and incremental loading
CREATE INDEX IF NOT EXISTS idx_raw_customers_customer_id
ON raw_layer.raw_customers (customer_id);

CREATE INDEX IF NOT EXISTS idx_raw_customers_updated_at
ON raw_layer.raw_customers (updated_at);

CREATE INDEX IF NOT EXISTS idx_raw_products_product_id
ON raw_layer.raw_products (product_id);

CREATE INDEX IF NOT EXISTS idx_raw_products_updated_at
ON raw_layer.raw_products (updated_at);

CREATE INDEX IF NOT EXISTS idx_raw_orders_order_id
ON raw_layer.raw_orders (order_id);

CREATE INDEX IF NOT EXISTS idx_raw_orders_customer_id
ON raw_layer.raw_orders (customer_id);

CREATE INDEX IF NOT EXISTS idx_raw_orders_order_date
ON raw_layer.raw_orders (order_date);

CREATE INDEX IF NOT EXISTS idx_raw_orders_updated_at
ON raw_layer.raw_orders (updated_at);

CREATE INDEX IF NOT EXISTS idx_raw_order_items_order_item_id
ON raw_layer.raw_order_items (order_item_id);

CREATE INDEX IF NOT EXISTS idx_raw_order_items_order_id
ON raw_layer.raw_order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_raw_order_items_product_id
ON raw_layer.raw_order_items (product_id);

CREATE INDEX IF NOT EXISTS idx_raw_order_items_updated_at
ON raw_layer.raw_order_items (updated_at);