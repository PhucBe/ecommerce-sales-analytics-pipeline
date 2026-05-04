with source as (
    select *
    from {{ source('raw', 'order_items') }}
),

cleaned as (
    select
        nullif(trim(order_item_id), '') as order_item_id,
        nullif(trim(order_id), '') as order_id,
        nullif(trim(product_id), '') as product_id,

        quantity::integer as quantity,
        unit_price::numeric(12, 2) as unit_price,
        coalesce(discount_amount, 0)::numeric(12, 2) as discount_amount,
        line_amount::numeric(12, 2) as line_amount,

        round(
            (
                quantity::numeric * unit_price::numeric
                - coalesce(discount_amount, 0)::numeric
            ),
            2
        ) as calculated_line_amount,

        round(
            (
                line_amount::numeric
                - (
                    quantity::numeric * unit_price::numeric
                    - coalesce(discount_amount, 0)::numeric
                )
            ),
            2
        ) as line_amount_diff,

        created_at::timestamptz as created_at,
        updated_at::timestamptz as updated_at,

        ingested_at::timestamptz as ingested_at
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by order_item_id
            order by updated_at desc nulls last, ingested_at desc nulls last
        ) as row_num
    from cleaned
    where order_item_id is not null
)

select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_amount,
    line_amount,
    calculated_line_amount,
    line_amount_diff,
    created_at,
    updated_at,
    ingested_at
from deduplicated
where row_num = 1