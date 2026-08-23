{{ config(materialized='table') }}

-- ticker
-- frame_year
-- frame_quarter
-- quarter_end
-- assets
-- assets_current
-- liabilities
-- liabilities_current
-- liabilities_and_stockholders_equity
-- cash
-- cash_and_cash_equivalents_at_carrying_value

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
    select * from {{ ref('edgar_cash_and_cash_equivalents_at_carrying_value') }}
)
pivot unioned on tag
using max(val) as val, max(form) as form
group by ticker, frame_year, frame_quarter, quarter_end
