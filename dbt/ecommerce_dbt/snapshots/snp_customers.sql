{% snapshot snp_customers %}

{{
    config(
        unique_key='customer_id',
        strategy='check',
        check_cols=[
            'city',
            'country',
            'customer_status',
            'email'
        ],
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}

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
from {{ ref('stg_customers') }}

{% endsnapshot %}