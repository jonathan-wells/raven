{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_operating_income_loss') }}
