{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_liabilities_and_stockholders_equity') }}
