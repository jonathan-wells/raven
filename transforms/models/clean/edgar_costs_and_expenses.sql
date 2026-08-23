{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_costs_and_expenses') }}
