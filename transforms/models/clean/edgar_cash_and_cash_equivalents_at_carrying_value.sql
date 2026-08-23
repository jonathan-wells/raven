{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_cash_and_cash_equivalents_at_carrying_value') }}
