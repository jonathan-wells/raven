{{ config(materialized='view') }}

with source_data as (

    select 1 as id
    union all
    select null as id

)

select *
from source_data

-- TODO: wire this up
-- create view totals as
-- select a.val as assets, l.val as liabilities, d.val as debt, (assets - liabilities) as value, a.ticker
-- from total_liabilities l
-- join total_assets a on a.accession_number == l.accession_number
-- join total_debt d on d.accession_number = a.accession_number;
