-- Check staging đã nhận version mới chưa
select
    customer_id,
    email,
    city,
    country,
    customer_status,
    updated_at,
    batch_id
from staging.stg_customers
where customer_id = 'CUST000001';

select
    product_id,
    category,
    brand,
    unit_price,
    cost,
    product_status,
    updated_at,
    batch_id
from staging.stg_products
where product_id = 'PROD000001';

-- Check lịch sử customers và products
select
    customer_id,
    email,
    city,
    country,
    customer_status,
    updated_at,
    dbt_valid_from,
    dbt_valid_to
from snapshots.snp_customers
where customer_id = 'CUST000001'
order by dbt_valid_from;

select
    product_id,
    category,
    brand,
    unit_price,
    cost,
    product_status,
    updated_at,
    dbt_valid_from,
    dbt_valid_to
from snapshots.snp_products
where product_id = 'PROD000001'
order by dbt_valid_from;

-- Check để chứng minh SCD2 đã hoạt động
select
    customer_id,
    count(*) as version_count,
    min(dbt_valid_from) as first_version_from,
    max(dbt_valid_from) as latest_version_from,
    count(*) filter (where dbt_valid_to is null) as current_version_count
from snapshots.snp_customers
group by customer_id
having count(*) > 1
order by version_count desc, customer_id;

select
    product_id,
    count(*) as version_count,
    min(dbt_valid_from) as first_version_from,
    max(dbt_valid_from) as latest_version_from,
    count(*) filter (where dbt_valid_to is null) as current_version_count
from snapshots.snp_products
group by product_id
having count(*) > 1
order by version_count desc, product_id;

-- Check mỗi business key chỉ có 1 current record
select
    customer_id,
    count(*) as current_count
from snapshots.snp_customers
where dbt_valid_to is null
group by customer_id
having count(*) > 1;

select
    product_id,
    count(*) as current_count
from snapshots.snp_products
where dbt_valid_to is null
group by product_id
having count(*) > 1;

-- Check không có version bị thiếu valid_from
select *
from snapshots.snp_customers
where dbt_valid_from is null;

select *
from snapshots.snp_products
where dbt_valid_from is null;

-- Check current records
select
    count(*) as current_customers
from snapshots.snp_customers
where dbt_valid_to is null;

select
    count(*) as current_products
from snapshots.snp_products
where dbt_valid_to is null;

-- Check số lượng current records nên bằng số dòng hiện tại trong staging
select count(*) from staging.stg_customers;
select count(*) from staging.stg_products;