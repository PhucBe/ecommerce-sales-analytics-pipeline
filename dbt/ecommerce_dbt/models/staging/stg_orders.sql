with source as (
    select *
    from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        nullif(trim(order_id), '') as order_id,
        nullif(trim(customer_id), '') as customer_id,

        order_date::date as order_date,
        order_date::timestamptz as order_timestamp,

        case
            when lower(trim(order_status)) in (
                'pending',
                'paid',
                'shipped',
                'completed',
                'cancelled',
                'refunded'
            )
                then lower(trim(order_status))
            else null
        end as order_status,

        case
            when lower(trim(payment_method)) in (
                'credit_card',
                'bank_transfer',
                'e_wallet',
                'cod'
            )
                then lower(trim(payment_method))
            else null
        end as payment_method,

        nullif(trim(shipping_city), '') as shipping_city,
        nullif(trim(shipping_country), '') as shipping_country,

        subtotal::numeric(12, 2) as subtotal,
        coalesce(discount_amount, 0)::numeric(12, 2) as discount_amount,
        coalesce(shipping_fee, 0)::numeric(12, 2) as shipping_fee,
        total_amount::numeric(12, 2) as total_amount,

        created_at::timestamptz as created_at,
        updated_at::timestamptz as updated_at,

        ingested_at::timestamptz as ingested_at
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by order_id
            order by updated_at desc nulls last, ingested_at desc nulls last
        ) as row_num
    from cleaned
    where order_id is not null
)

select
    order_id,
    customer_id,
    order_date,
    order_timestamp,
    order_status,
    payment_method,
    shipping_city,
    shipping_country,
    subtotal,
    discount_amount,
    shipping_fee,
    total_amount,
    created_at,
    updated_at,
    ingested_at
from deduplicated
where row_num = 1