with source as (
    select *
    from {{ source('raw', 'products') }}
),

cleaned as (
    select
        nullif(trim(product_id), '') as product_id,
        nullif(trim(product_name), '') as product_name,
        nullif(trim(category), '') as category,
        nullif(trim(brand), '') as brand,

        unit_price::numeric(12, 2) as unit_price,
        cost::numeric(12, 2) as cost,

        case
            when lower(trim(product_status)) in ('active', 'inactive', 'discontinued')
                then lower(trim(product_status))
            else null
        end as product_status,

        created_at::timestamptz as created_at,
        updated_at::timestamptz as updated_at,

        ingested_at::timestamptz as ingested_at,
        nullif(trim(batch_id), '') as batch_id,
        nullif(trim(source_system), '') as source_system
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by product_id
            order by updated_at desc nulls last, ingested_at desc nulls last
        ) as row_num
    from cleaned
    where product_id is not null
)

select
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
    source_system
from deduplicated
where row_num = 1