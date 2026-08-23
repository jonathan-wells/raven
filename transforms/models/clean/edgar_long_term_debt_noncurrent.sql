{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_long_term_debt_noncurrent') }}
