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

    case
        when assets_val is not null
            then assets_val
        when assets_val is null
            and liabilities_and_stockholders_equity_val is not null
            then liabilities_and_stockholders_equity_val
        when assets_val is null
            and liabilities_and_stockholders_equity_val is null
            and liabilities_val is not null
            and stockholders_equity_val is not null
            then liabilities_val + stockholders_equity_val
        else null
    end as assets,

    case
        when liabilities_val is not null
            then liabilities_val
        when liabilities_val is null
            and liabilities_and_stockholders_equity_val is not null
            and stockholders_equity_val is not null
            then liabilities_and_stockholders_equity_val - stockholders_equity_val
        else null
    end as liabilities,

    case
        when stockholders_equity_val is not null
            then stockholders_equity_val
        when stockholders_equity_val is null
            and liabilities_val is not null
            and assets_val is not null
            then assets_val - liabilities_val
        else null
    end as stockholders_equity,

    case
        when liabilities_and_stockholders_equity_val is not null
            then liabilities_and_stockholders_equity_val
        when liabilities_and_stockholders_equity_val is null
            and assets_val is not null
            then assets_val
        when liabilities_and_stockholders_equity_val is null
            and assets_val is null
            and liabilities_val is not null
            and stockholders_equity_val is not null
            then liabilities_val + stockholders_equity_val
        else null
    end as liabilities_and_stockholders_equity,

    assets_current_val as assets_current,
    liabilities_current_val as liabilities_current,
    cash_and_cash_equivalents_at_carrying_value_val as cash_and_cash_equivalents_at_carrying_value,

    case
        when assets is null
            and liabilities is null
            and liabilities_and_stockholders_equity is null
            then false
        when liabilities is null
            and stockholders_equity is null
            and liabilities_and_stockholders_equity is null
            then false
        when assets == liabilities_and_stockholders_equity
            and assets is not null
            then true
        when assets == liabilities + stockholders_equity
            and assets is not null
            then true
        else false
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
