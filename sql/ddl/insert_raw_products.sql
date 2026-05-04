insert into raw_layer.raw_products (
    product_id,
    product_name,
    category,
    brand,
    unit_price,
    cost,
    product_status,
    created_at,
    updated_at,
    ingested_at,
    batch_id,
    source_system,
    raw_payload
)
select
    product_id,
    product_name,
    category,
    brand,
    unit_price + 10.00 as unit_price,
    cost + 3.00 as cost,
    'inactive' as product_status,
    created_at,
    updated_at + interval '1 day' as updated_at,
    current_timestamp as ingested_at,
    'manual_scd2_test_products' as batch_id,
    source_system,
    raw_payload
from raw_layer.raw_products
where product_id = 'PROD000001'
order by updated_at desc nulls last, ingested_at desc nulls last
limit 1;