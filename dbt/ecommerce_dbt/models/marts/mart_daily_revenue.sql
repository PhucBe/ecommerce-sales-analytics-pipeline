{{ config(materialized='table') }}

with orders as (
    select
        order_id,
        customer_id,
        order_date::date as order_date,
        order_status,
        subtotal,
        total_amount
    from {{ ref('fct_orders') }}
    where order_status in ('paid', 'shipped', 'completed')
),

daily_revenue as (
    select
        order_date,
        count(distinct order_id) as order_count,
        count(distinct customer_id) as customer_count,
        sum(subtotal)::numeric(12, 2) as gross_revenue,
        sum(total_amount)::numeric(12, 2) as net_revenue,
        (sum(total_amount) / nullif(count(distinct order_id), 0))::numeric(12, 2) as avg_order_value
    from orders
    group by order_date
)

select *
from daily_revenue