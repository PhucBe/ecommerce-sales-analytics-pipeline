with source as (
    select *
    from {{ source('raw', 'customers') }}
),

cleaned as (
    select
        nullif(trim(customer_id), '') as customer_id,
        nullif(trim(customer_name), '') as customer_name,
        lower(nullif(trim(email), '')) as email,
        nullif(trim(phone), '') as phone,
        nullif(trim(city), '') as city,
        nullif(trim(country), '') as country,

        case
            when lower(trim(customer_status)) in ('active', 'inactive', 'churned')
                then lower(trim(customer_status))
            else null
        end as customer_status,

        created_at::timestamptz as created_at,
        updated_at::timestamptz as updated_at,

        ingested_at::timestamptz as ingested_at
    from source
),

deduplicated as (
    select
        *,
        row_number() over(
            partition by customer_id
            order by updated_at desc nulls last, ingested_at desc nulls last
        ) as row_num
    from cleaned
    where customer_id is not null
)

select
    customer_id,
    customer_name,
    email,
    phone,
    city,
    country,
    customer_status,
    created_at,
    updated_at,
    ingested_at
from deduplicated
where row_num = 1