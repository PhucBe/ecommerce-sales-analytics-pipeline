{{ config(materialized='table') }}

with order_items as (
    select
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount_amount,
        line_amount,
        created_at,
        updated_at,
        ingested_at
    from {{ ref('stg_order_items') }}
),

orders as (
    select
        order_id,
        customer_id,
        order_date,
        order_status,
        payment_method,
        shipping_city,
        shipping_country
    from {{ ref('stg_orders') }}
),

customers as (
    select
        customer_version_sk,
        customer_id,
        valid_from,
        valid_to
    from {{ ref('dim_customer') }}

),

products as (
    select
        product_version_sk,
        product_id,
        unit_price as product_unit_price_at_order,
        cost as product_cost_at_order,
        valid_from,
        valid_to
    from {{ ref('dim_product') }}
),

final as (
    select
        oi.order_item_id,
        oi.order_id,

        o.customer_id,
        c.customer_version_sk,

        oi.product_id,
        p.product_version_sk,

        o.order_date,
        o.order_status,
        o.payment_method,
        o.shipping_city,
        o.shipping_country,

        oi.quantity,
        oi.unit_price as sold_unit_price,
        oi.discount_amount as item_discount_amount,
        oi.line_amount,

        p.product_unit_price_at_order,
        p.product_cost_at_order,

        (oi.quantity * p.product_cost_at_order)::numeric(12, 2) as estimated_cost_amount,
        (oi.line_amount - (oi.quantity * p.product_cost_at_order))::numeric(12, 2) as estimated_gross_margin_amount,
        
        oi.created_at as order_item_created_at,
        oi.updated_at as order_item_updated_at,
        oi.ingested_at

    from order_items oi
    left join orders o
        on oi.order_id = o.order_id
    left join customers c
        on o.customer_id = c.customer_id
        and o.order_date::timestamp >= c.valid_from
        and o.order_date::timestamp < c.valid_to
    left join products p
        on oi.product_id = p.product_id
        and o.order_date::timestamp >= p.valid_from
        and o.order_date::timestamp < p.valid_to
)

select *
from final