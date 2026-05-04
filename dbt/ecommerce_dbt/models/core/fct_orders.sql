{{ config(materialized='table') }}

with orders as (
    select
        order_id,
        customer_id,
        order_date,
        order_status,
        payment_method,
        shipping_city,
        shipping_country,
        subtotal,
        discount_amount,
        shipping_fee,
        total_amount,
        created_at,
        updated_at,
        ingested_at
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

final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_version_sk,
        o.order_date,
        o.order_status,
        o.payment_method,
        o.shipping_city,
        o.shipping_country,
        o.subtotal,
        o.discount_amount,
        o.shipping_fee,
        o.total_amount,
        o.created_at as order_created_at,
        o.updated_at as order_updated_at,
        o.ingested_at
    from orders o
    left join customers c
        on o.customer_id = c.customer_id
        and o.order_date::timestamp >= c.valid_from
        and o.order_date::timestamp < c.valid_to

)

select *
from final