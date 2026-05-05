--
select *
from marts.mart_daily_revenue
order by order_date
limit 20;

select *
from marts.mart_top_products
order by revenue desc
limit 20;

select *
from marts.mart_customer_retention
order by total_revenue desc
limit 20;

select *
from marts.mart_customer_churn
order by days_since_last_order desc
limit 20;

--
select
    sum(net_revenue) as mart_net_revenue
from marts.mart_daily_revenue;

select
    sum(total_amount) as fact_net_revenue
from core.fct_orders
where order_status in ('paid', 'shipped', 'completed');

--
select
    sum(revenue) as mart_product_revenue
from marts.mart_top_products;

select
    sum(line_amount) as fact_item_revenue
from core.fct_order_items
where order_status in ('paid', 'shipped', 'completed');

--
select
    is_repeat_customer,
    count(*) as customer_count
from marts.mart_customer_retention
group by is_repeat_customer
order by is_repeat_customer desc;

--
select
    churn_flag_30d,
    churn_flag_60d,
    churn_flag_90d,
    count(*) as customer_count
from marts.mart_customer_churn
group by
    churn_flag_30d,
    churn_flag_60d,
    churn_flag_90d
order by
    churn_flag_30d desc,
    churn_flag_60d desc,
    churn_flag_90d desc;