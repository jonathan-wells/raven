{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_stockholders_equity') }}
