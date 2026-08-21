{{ config(materialized='view', schema='clean') }}
{{ clean_edgar_input(
    'edgar_total_assets',
    [
        "Assets",
    ]
) }}
