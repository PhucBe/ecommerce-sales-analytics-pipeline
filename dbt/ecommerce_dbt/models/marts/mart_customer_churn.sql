{{ config(materialized='table') }}

with customer_retention as (
    select
        customer_id,
        last_order_date,
        total_orders,
        total_revenue
    from {{ ref('mart_customer_retention') }}
),

analysis_date as (
    select
        max(last_order_date) as as_of_date
    from customer_retention
),

customer_churn as (
    select
        cr.customer_id,
        cr.last_order_date,
        (ad.as_of_date - cr.last_order_date) as days_since_last_order,

        case
            when (ad.as_of_date - cr.last_order_date) > 30 then true
            else false
        end as churn_flag_30d,

        case
            when (ad.as_of_date - cr.last_order_date) > 60 then true
            else false
        end as churn_flag_60d,

        case
            when (ad.as_of_date - cr.last_order_date) > 90 then true
            else false
        end as churn_flag_90d,

        cr.total_orders as lifetime_orders,
        cr.total_revenue as lifetime_revenue
    from customer_retention cr
    cross join analysis_date ad
)

select *
from customer_churn