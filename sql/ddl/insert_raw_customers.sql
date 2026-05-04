insert into raw_layer.raw_customers (
    customer_id,
    customer_name,
    email,
    phone,
    city,
    country,
    customer_status,
    created_at,
    updated_at,
    ingested_at,
    batch_id,
    source_system,
    raw_payload
)
select
    customer_id,
    customer_name,
    'new1@example.net' as email,
    phone,
    'Ho Chi Minh City' as city,
    country,
    'active' as customer_status,
    created_at,
    updated_at + interval '1 day' as updated_at,
    current_timestamp as ingested_at,
    'manual_scd2_test_customers' as batch_id,
    source_system,
    raw_payload
from raw_layer.raw_customers
where customer_id = 'CUST000001'
order by updated_at desc nulls last, ingested_at desc nulls last
limit 1;