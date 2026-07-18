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
    r.val as revenue,
    a.ticker as ticker,
    a.accession_number as accession_number,
    a.end as end_date
from total_liabilities l
left outer join total_assets a on a.accession_number = l.accession_number
left outer join total_debt d on d.accession_number = a.accession_number
left outer join revenue r on r.accession_number = a.accession_number
