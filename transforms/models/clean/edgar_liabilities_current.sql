{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_liabilities_current') }}
