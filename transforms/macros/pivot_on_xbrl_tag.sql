{% macro pivot_on_xbrl_tag(cte_table) -%}

pivot {{ cte_table }} on tag
using max(val) as val, max(form) as form
group by ticker, frame_year, frame_quarter, quarter_end

{%- endmacro %}
