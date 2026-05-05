{{ config(materialized='table') }}

with orders as (
    select
        order_id,
        customer_id,
        order_date::date as order_date,
        total_amount
    from {{ ref('fct_orders') }}
    where order_status in ('paid', 'shipped', 'completed')
),

customer_orders as (
    select
        customer_id,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        count(distinct order_id) as total_orders,
        sum(total_amount)::numeric(12, 2) as total_revenue
    from orders
    group by customer_id
),

final as (
    select
        customer_id,
        first_order_date,
        last_order_date,
        total_orders,
        total_revenue,
        case
            when total_orders >= 2 then true
            else false
        end as is_repeat_customer
    from customer_orders
)

select *
from final