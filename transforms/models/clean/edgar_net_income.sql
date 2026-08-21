{{ config(materialized='view', schema='clean') }}
{{ clean_edgar_input(
    'edgar_net_income',
    [
        "NetIncomeLoss",
    ]
) }}
