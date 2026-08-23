{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_cost_of_revenue') }}
