{{ config(materialized='view', schema='clean') }}
{{ clean_edgar_input(
    'edgar_gross_profit',
    [
        "GrossProfit",
    ]
) }}
