-- 
select count(*) as row_count
from staging.stg_customers;

select count(*) as row_count
from staging.stg_products;

select count(*) as row_count
from staging.stg_orders;

select count(*) as row_count
from staging.stg_order_items;

-- Check status
select customer_status, count(*) as row_count
from staging.stg_customers
group by customer_status
order by row_count desc;

select product_status, count(*) as row_count
from staging.stg_products
group by product_status
order by row_count desc;

select order_status, count(*) as row_count
from staging.stg_orders
group by order_status
order by row_count desc;

-- Check line amount
select *
from staging.stg_order_items
where abs(line_amount_diff) > 0.01
limit 20;

-- Check duplicate
select customer_id, count(*) as row_count
from staging.stg_customers
group by customer_id
having count(*) > 1;

select product_id, count(*) as row_count
from staging.stg_products
group by product_id
having count(*) > 1;

select order_id, count(*) as row_count
from staging.stg_orders
group by order_id
having count(*) > 1;

select order_item_id, count(*) as row_count
from staging.stg_order_items
group by order_item_id
having count(*) > 1;