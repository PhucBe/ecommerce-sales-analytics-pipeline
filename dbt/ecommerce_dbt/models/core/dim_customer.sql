{{ config(materialized='table') }}

with snapshot_data as (
    select
        dbt_scd_id as customer_version_sk,
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
        dbt_valid_from,
        dbt_valid_to,
        row_number() over (
            partition by customer_id
            order by dbt_valid_from
        ) as customer_version_number
    from {{ ref('snp_customers') }}
),

final as (
    select
        customer_version_sk,
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

        case
            when customer_version_number = 1
                then timestamp '1900-01-01'
            else dbt_valid_from
        end as valid_from,

        coalesce(dbt_valid_to, timestamp '9999-12-31') as valid_to,

        case
            when dbt_valid_to is null then true
            else false
        end as is_current,

        customer_version_number
    from snapshot_data

)

select *
from final