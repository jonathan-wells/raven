{{ config(materialized='view') }}

with revenue as (
    select *
    from {{ source('raw', 'income_revenue') }}
),
gross_profit as (
    select *
    from {{ source('raw', 'income_gross_profit') }}
),
operating_income as (
    select *
    from {{ source('raw', 'income_operating_income') }}
),
net_income as (
    select *
    from {{ source('raw', 'income_net_income') }}
),
cost_of_revenue as (
    select *
    from {{ source('raw', 'income_cost_of_revenue') }}
)

select
    coalesce(r.dataset, g.dataset, o.dataset, n.dataset) as dataset,
    coalesce(r.ticker, g.ticker, o.ticker, n.ticker) as ticker,
    coalesce(r.end, g.end, o.end, n.end) as end_date,
    coalesce(r.filed, g.filed, o.filed, n.filed) as filing_date,
    coalesce(r.form, g.form, o.form, n.form) as form,
    r.val as revenue,
    g.val as gross_profit,
    o.val as operating_income,
    n.val as net_income,
    c.val as cost_of_revenue
from revenue r
full outer join gross_profit g
    on r.ticker = g.ticker
    and r.end = g.end
full outer join operating_income o
    on coalesce(r.ticker, g.ticker) = o.ticker
    and coalesce(r.end, g.end) = o.end
full outer join net_income n
    on coalesce(r.ticker, g.ticker, o.ticker) = n.ticker
    and coalesce(r.end, g.end, o.end) = n.end
full outer join cost_of_revenue c
    on coalesce(r.ticker, g.ticker, o.ticker, n.ticker) = c.ticker
    and coalesce(r.end, g.end, o.end, n.end) = c.end
