{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_revenue_from_contract_with_customer_excluding_assessed_tax') }}
