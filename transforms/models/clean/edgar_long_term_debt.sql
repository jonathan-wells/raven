{{ config(materialized='view', schema='clean') }}
{{ clean_edgar_input(
    'edgar_long_term_debt',
    [
        "LongTermDebtNoncurrent",
    ]
) }}
