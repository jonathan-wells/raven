{{ config(materialized='view') }}
{{ clean_edgar_input('edgar_sales_revenue_goods_gross') }}
