{% macro clean_edgar_input(source_table) -%}
with facts as (
    select
        *
    from {{ source('raw', source_table) }}
),

-- Quarter classification: frame is 'CYyyyy' for annual facts, 'CYyyyyQn' for
-- quarterly facts.
classified as (
    select
        *,
        regexp_extract(frame, 'CY(\d+)', 1)::int as frame_year,
        coalesce(nullif(regexp_extract(frame, 'CY\d+(Q\d)', 1), ''), 'FY') as frame_quarter
    from facts
),

pivoted as (
    select
        ticker,
        frame_year,
        max(case when frame_quarter = 'Q1' then val end) as q1_val,
        max(case when frame_quarter = 'Q2' then val end) as q2_val,
        max(case when frame_quarter = 'Q3' then val end) as q3_val,
        max(case when frame_quarter = 'FY' then val end) as fy_val,
        max(case when frame_quarter = 'FY' then "end" end) as fy_end,
        max(case when frame_quarter = 'FY' then filed end) as fy_filed,
        max(case when frame_quarter = 'FY' then form end) as fy_form
    from classified
    group by ticker, frame_year
),

-- Q4 is rarely reported directly: derive it as FY - (Q1+Q2+Q3), only when all
-- four figures are present for that ticker/year.
derived_q4 as (
    select
        ticker,
        frame_year,
        'Q4' as frame_quarter,
        fy_val - (q1_val + q2_val + q3_val) as val,
        fy_end as "end",
        fy_filed as filed,
        fy_form as form
    from pivoted
    where q1_val is not null
        and q2_val is not null
        and q3_val is not null
        and fy_val is not null
)

-- Output is quarterly only (Q1-Q4): FY shares its "end" date with Q4, and
-- downstream consumers join on (ticker, end), so keeping both would duplicate
-- that key. Some filers do report a genuine Q4 frame directly, but not
-- consistently, so Q4 is always taken from derived_q4 (dropped entirely when
-- it can't be derived) rather than mixed with raw Q4 frames, which would
-- otherwise duplicate the (ticker, frame_year, 'Q4') grain.
select ticker, frame_year, frame_quarter, val, "end", filed, form
from classified
where frame_quarter not in ('Q4', 'FY')

union all

select ticker, frame_year, frame_quarter, val, "end", filed, form
from derived_q4
{%- endmacro %}
