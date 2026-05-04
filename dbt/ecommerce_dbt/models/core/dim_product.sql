{{ config(materialized='table') }}

with snapshot_data as (
    select
        dbt_scd_id as product_version_sk,
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
        dbt_valid_from,
        dbt_valid_to,
        row_number() over (
            partition by product_id
            order by dbt_valid_from
        ) as product_version_number
    from {{ ref('snp_products') }}

),

final as (
    select
        product_version_sk,
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

        case
            when product_version_number = 1
                then timestamp '1900-01-01'
            else dbt_valid_from
        end as valid_from,

        coalesce(dbt_valid_to, timestamp '9999-12-31') as valid_to,

        case
            when dbt_valid_to is null then true
            else false
        end as is_current,

        product_version_number
    from snapshot_data
)

select *
from final