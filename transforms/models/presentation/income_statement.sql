{{ config(materialized='table') }}

with unioned_revenues as (
    select * from {{ ref('edgar_revenue_from_contract_with_customer_excluding_assessed_tax') }}
    union all
    select * from {{ ref('edgar_revenues')}}
    union all
    select * from {{ ref('edgar_sales_revenue_net')}}
    union all
    select * from {{ ref('edgar_sales_revenue_goods_net')}}
    union all
    select * from {{ ref('edgar_sales_revenue_services_net')}}
    union all
    select * from {{ ref('edgar_sales_revenue_goods_gross')}}
),

pivoted_revenues as (
    select
        *,
        coalesce(
            revenue_from_contract_with_customer_excluding_assessed_tax_val,
            revenues_val,
            sales_revenue_net_val,
            sales_revenue_goods_net_val,
            sales_revenue_services_net_val,
            sales_revenue_goods_gross_val
        ) as estimated_total_revenue,
        case
            when revenue_from_contract_with_customer_excluding_assessed_tax_val is not null
                then 'revenue_from_contract_with_customer_excluding_assessed_tax'
            when revenues_val is not null
                then 'revenues'
            when sales_revenue_net_val is not null
                then 'sales_revenue_net'
            when sales_revenue_goods_net_val is not null
                then 'sales_revenue_goods_net'
            when sales_revenue_services_net_val is not null
                then 'sales_revenue_services_net'
            when sales_revenue_goods_gross_val is not null
                then 'sales_revenue_goods_gross'
        end as estimated_total_revenue_tag
    from ({{ pivot_on_xbrl_tag('unioned_revenues') }})
),

unioned_cost_of_revenue as (
    select * from {{ ref('edgar_cost_of_revenue')}}
    union all
    select * from {{ ref('edgar_cost_of_goods_and_services_sold')}}
),

pivoted_cost_of_revenue as (
    select
        *,
        coalesce(
            cost_of_revenue_val,
            cost_of_goods_and_services_sold_val
        ) as estimated_cost_of_revenue,
        case
            when cost_of_revenue_val is not null
                then 'cost_of_revenue'
            when cost_of_goods_and_services_sold_val is not null
                then 'cost_of_goods_and_services_sold'
        end as estimated_cost_of_revenue_tag
    from ({{ pivot_on_xbrl_tag('unioned_cost_of_revenue') }})
),

unioned_operating_expenses as (
    select * from {{ ref('edgar_operating_expenses')}}
    union all
    select * from {{ ref('edgar_costs_and_expenses')}}
),

pivoted_operating_expenses as (
    select
        *,
        coalesce(
            operating_expenses_val,
            costs_and_expenses_val
        ) as estimated_operating_expenses,
        case
            when operating_expenses_val is not null
                then 'operating_expenses'
            when costs_and_expenses_val is not null
                then 'costs_and_expenses'
        end as estimated_operating_expenses_tag
    from ({{ pivot_on_xbrl_tag('unioned_operating_expenses') }})
)

select
    *
from pivoted_revenues
full outer join pivoted_cost_of_revenue
    using (ticker, frame_year, frame_quarter, quarter_end)
full outer join pivoted_operating_expenses
    using (ticker, frame_year, frame_quarter, quarter_end)
full outer join ({{ pivot_on_xbrl_tag(ref('edgar_operating_income_loss')) }})
    using (ticker, frame_year, frame_quarter, quarter_end)
full outer join ({{ pivot_on_xbrl_tag(ref('edgar_net_income_loss')) }})
    using (ticker, frame_year, frame_quarter, quarter_end)
full outer join ({{ pivot_on_xbrl_tag(ref('edgar_gross_profit')) }})
    using (ticker, frame_year, frame_quarter, quarter_end)
order by ticker, frame_year, frame_quarter
