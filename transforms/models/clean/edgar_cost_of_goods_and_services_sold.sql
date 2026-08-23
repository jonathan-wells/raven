{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_cost_of_goods_and_services_sold') }}
