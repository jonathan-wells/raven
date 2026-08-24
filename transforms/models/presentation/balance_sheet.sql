{{ config(materialized='table') }}

with unioned as (
    select * from {{ ref('edgar_assets') }}
    union all
    select * from {{ ref('edgar_assets_current') }}
    union all
    select * from {{ ref('edgar_liabilities') }}
    union all
    select * from {{ ref('edgar_liabilities_current') }}
    union all
    select * from {{ ref('edgar_liabilities_and_stockholders_equity') }}
    union all
    select * from {{ ref('edgar_stockholders_equity') }}
    union all
    select * from {{ ref('edgar_cash_and_cash_equivalents_at_carrying_value') }}
),

pivoted as (
    pivot unioned on tag
    using max(val) as val, max(form) as form
    group by ticker, frame_year, frame_quarter, quarter_end
)

select
    ticker,
    frame_year,
    frame_quarter,
    quarter_end,
    assets_val as assets,
    assets_current_val as assets_current,
    liabilities_val as liabilities,
    liabilities_current_val as liabilities_current,
    liabilities_and_stockholders_equity_val as liabilities_and_stockholders_equity,
    stockholders_equity_val as stockholders_equity,
    cash_and_cash_equivalents_at_carrying_value_val as cash_and_cash_equivalents_at_carrying_value,
    case
        when assets != liabilities_and_stockholders_equity then false
        else true
    end as is_reconciled,
    assets_form,
    assets_current_form,
    liabilities_form,
    liabilities_current_form,
    liabilities_and_stockholders_equity_form,
    stockholders_equity_form,
    cash_and_cash_equivalents_at_carrying_value_form
from pivoted
order by ticker, frame_year, frame_quarter
