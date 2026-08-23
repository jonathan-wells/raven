{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_net_income_loss') }}
