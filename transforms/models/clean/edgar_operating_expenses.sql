{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_operating_expenses') }}
