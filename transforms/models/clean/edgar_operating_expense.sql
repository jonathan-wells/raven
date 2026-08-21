{{ config(materialized='view', schema='clean') }}
{{ clean_edgar_input(
    'edgar_operating_expense',
    [
        "OperatingExpenses",
        "CostsAndExpenses",
    ]
) }}
