with checks as (
    -- 1. mart_daily_revenue should not be empty
    select
        'mart_daily_revenue_empty' as check_name,
        case
            when count(*) = 0 then 1
            else 0
        end as failed_count
    from marts.mart_daily_revenue

    union all

    -- 2. Revenue metrics should not be negative
    select
        'daily_revenue_negative_values' as check_name,
        count(*) as failed_count
    from marts.mart_daily_revenue
    where gross_revenue < 0
       or net_revenue < 0
       or avg_order_value < 0

    union all

    -- 3. Average order value should equal net_revenue / order_count
    select
        'daily_revenue_aov_mismatch' as check_name,
        count(*) as failed_count
    from marts.mart_daily_revenue
    where round(avg_order_value, 2)
       <> round(net_revenue / nullif(order_count, 0), 2)

    union all

    -- 4. Order count and customer count should be positive
    select
        'daily_revenue_non_positive_counts' as check_name,
        count(*) as failed_count
    from marts.mart_daily_revenue
    where order_count <= 0
       or customer_count <= 0

    union all

    -- 5. Product mart should not be empty
    select
        'mart_top_products_empty' as check_name,
        case
            when count(*) = 0 then 1
            else 0
        end as failed_count
    from marts.mart_top_products

    union all

    -- 6. Product metrics should not be negative
    select
        'top_products_negative_values' as check_name,
        count(*) as failed_count
    from marts.mart_top_products
    where units_sold < 0
       or order_count < 0
       or revenue < 0

    union all

    -- 7. Customer retention mart should not be empty
    select
        'mart_customer_retention_empty' as check_name,
        case
            when count(*) = 0 then 1
            else 0
        end as failed_count
    from marts.mart_customer_retention

    union all

    -- 8. First order date should not be after last order date
    select
        'retention_invalid_date_range' as check_name,
        count(*) as failed_count
    from marts.mart_customer_retention
    where first_order_date > last_order_date

    union all

    -- 9. Repeat customer flag should match total_orders >= 2
    select
        'retention_repeat_flag_mismatch' as check_name,
        count(*) as failed_count
    from marts.mart_customer_retention
    where is_repeat_customer <> case
        when total_orders >= 2 then true
        else false
    end

    union all

    -- 10. Customer total orders and revenue should not be negative
    select
        'retention_negative_values' as check_name,
        count(*) as failed_count
    from marts.mart_customer_retention
    where total_orders < 0
       or total_revenue < 0

    union all

    -- 11. Customer churn mart should not be empty
    select
        'mart_customer_churn_empty' as check_name,
        case
            when count(*) = 0 then 1
            else 0
        end as failed_count
    from marts.mart_customer_churn

    union all

    -- 12. Days since last order should not be negative
    select
        'churn_negative_days_since_last_order' as check_name,
        count(*) as failed_count
    from marts.mart_customer_churn
    where days_since_last_order < 0

    union all

    -- 13. Churn 30d flag should match days_since_last_order > 30
    select
        'churn_flag_30d_mismatch' as check_name,
        count(*) as failed_count
    from marts.mart_customer_churn
    where churn_flag_30d <> case
        when days_since_last_order > 30 then true
        else false
    end

    union all

    -- 14. Churn 60d flag should match days_since_last_order > 60
    select
        'churn_flag_60d_mismatch' as check_name,
        count(*) as failed_count
    from marts.mart_customer_churn
    where churn_flag_60d <> case
        when days_since_last_order > 60 then true
        else false
    end

    union all

    -- 15. Churn 90d flag should match days_since_last_order > 90
    select
        'churn_flag_90d_mismatch' as check_name,
        count(*) as failed_count
    from marts.mart_customer_churn
    where churn_flag_90d <> case
        when days_since_last_order > 90 then true
        else false
    end
)

select *
from checks
order by check_name;