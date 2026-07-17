{{ config(materialized='view') }}

with total_assets as (
    select *
    from {{ source('raw', 'total_assets') }}
),
total_liabilities as (
    select *
    from {{ source('raw', 'total_liabilities') }}
),
total_debt as (
    select *
    from {{ source('raw', 'total_debt') }}
),
revenue as (
    select *
    from {{ source('raw', 'revenue') }}
)
select
    a.val as assets,
    l.val as liabilities,
    d.val as debt,
    r.val as revenue
from total_liabilities l
join total_assets a on a.accession_number = l.accession_number
join total_debt d on d.accession_number = a.accession_number
join revenue r on r.accession_number = a.accession_number
