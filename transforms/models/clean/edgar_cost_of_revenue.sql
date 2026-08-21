{{ config(materialized='view', schema='clean') }}
{{ clean_edgar_input(
    'edgar_cost_of_revenue',
    [
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold",
    ],

) }}
