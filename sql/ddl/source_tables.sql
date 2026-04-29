-- =========================================================
-- Source Tables DDL
-- Project: E-Commerce Sales Analytics
-- Purpose:
--   Define source schema for mock e-commerce API.
--
-- Note:
--   These are source-like tables used as schema contract.
--   Raw ingestion tables will be created separately in Phase 4.
-- =========================================================

CREATE SCHEMA IF NOT EXISTS source;

-- =========================================================
-- 1. customers
-- Grain: 1 row per customer
-- =========================================================

DROP TABLE IF EXISTS source.customers CASCADE;

CREATE TABLE source.customers (
    customer_id VARCHAR(50) PRIMARY KEY,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),

    gender VARCHAR(20),
    birth_date DATE,

    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,

    customer_status VARCHAR(30) NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    CONSTRAINT chk_customers_status
        CHECK (customer_status IN ('active', 'inactive', 'blocked')),

    CONSTRAINT chk_customers_updated_after_created
        CHECK (updated_at >= created_at)
);

-- =========================================================
-- 2. products
-- Grain: 1 row per product
-- =========================================================

DROP TABLE IF EXISTS source.products CASCADE;

CREATE TABLE source.products (
    product_id VARCHAR(50) PRIMARY KEY,

    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),

    unit_price NUMERIC(12, 2) NOT NULL,
    cost NUMERIC(12, 2) NOT NULL,

    product_status VARCHAR(30) NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    CONSTRAINT chk_products_unit_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_products_cost
        CHECK (cost >= 0),

    CONSTRAINT chk_products_status
        CHECK (product_status IN ('active', 'inactive', 'discontinued')),

    CONSTRAINT chk_products_updated_after_created
        CHECK (updated_at >= created_at)
);

-- =========================================================
-- 3. orders
-- Grain: 1 row per order
-- =========================================================

DROP TABLE IF EXISTS source.orders CASCADE;

CREATE TABLE source.orders (
    order_id VARCHAR(50) PRIMARY KEY,

    customer_id VARCHAR(50) NOT NULL,
    order_date TIMESTAMP NOT NULL,

    order_status VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',

    subtotal_amount NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    shipping_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(12, 2) NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES source.customers (customer_id),

    CONSTRAINT chk_orders_status
        CHECK (order_status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled', 'returned')),

    CONSTRAINT chk_orders_payment_status
        CHECK (payment_status IN ('unpaid', 'paid', 'refunded', 'failed')),

    CONSTRAINT chk_orders_subtotal_amount
        CHECK (subtotal_amount >= 0),

    CONSTRAINT chk_orders_discount_amount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_orders_shipping_amount
        CHECK (shipping_amount >= 0),

    CONSTRAINT chk_orders_tax_amount
        CHECK (tax_amount >= 0),

    CONSTRAINT chk_orders_total_amount
        CHECK (total_amount >= 0),

    CONSTRAINT chk_orders_updated_after_created
        CHECK (updated_at >= created_at)
);

-- =========================================================
-- 4. order_items
-- Grain: 1 row per product inside 1 order
-- =========================================================

DROP TABLE IF EXISTS source.order_items CASCADE;

CREATE TABLE source.order_items (
    order_item_id VARCHAR(50) PRIMARY KEY,

    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,

    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    line_amount NUMERIC(12, 2) NOT NULL,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES source.orders (order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES source.products (product_id),

    CONSTRAINT chk_order_items_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_order_items_unit_price
        CHECK (unit_price >= 0),

    CONSTRAINT chk_order_items_discount_amount
        CHECK (discount_amount >= 0),

    CONSTRAINT chk_order_items_line_amount
        CHECK (line_amount >= 0),

    CONSTRAINT chk_order_items_updated_after_created
        CHECK (updated_at >= created_at)
);

-- =========================================================
-- Indexes
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
    ON source.orders (customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_order_date
    ON source.orders (order_date);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id
    ON source.order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
    ON source.order_items (product_id);

CREATE INDEX IF NOT EXISTS idx_customers_updated_at
    ON source.customers (updated_at);

CREATE INDEX IF NOT EXISTS idx_products_updated_at
    ON source.products (updated_at);

CREATE INDEX IF NOT EXISTS idx_orders_updated_at
    ON source.orders (updated_at);

CREATE INDEX IF NOT EXISTS idx_order_items_updated_at
    ON source.order_items (updated_at);