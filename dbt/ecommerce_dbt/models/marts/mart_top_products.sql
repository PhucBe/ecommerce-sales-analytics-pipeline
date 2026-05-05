{{ config(materialized='table') }}

with order_items as (
    select
        order_item_id,
        order_id,
        product_id,
        product_version_sk,
        order_status,
        quantity,
        line_amount
    from {{ ref('fct_order_items') }}
    where order_status in ('paid', 'shipped', 'completed')
),

products as (
    select
        product_version_sk,
        product_id,
        product_name,
        category
    from {{ ref('dim_product') }}
),

product_sales as (
    select
        oi.product_id,
        coalesce(p.product_name, 'unknown') as product_name,
        coalesce(p.category, 'unknown') as category,
        sum(oi.quantity)::integer as units_sold,
        count(distinct oi.order_id) as order_count,
        sum(oi.line_amount)::numeric(12, 2) as revenue
    from order_items oi
    left join products p
        on oi.product_version_sk = p.product_version_sk
    group by
        oi.product_id,
        coalesce(p.product_name, 'unknown'),
        coalesce(p.category, 'unknown')
)

select *
from product_sales