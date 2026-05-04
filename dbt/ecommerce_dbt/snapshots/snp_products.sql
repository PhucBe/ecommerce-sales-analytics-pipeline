{% snapshot snp_products %}

{{
    config(
        unique_key='product_id',
        strategy='check',
        check_cols=[
            'category',
            'brand',
            'unit_price',
            'cost',
            'product_status'
        ],
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

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
from {{ ref('stg_products') }}

{% endsnapshot %}