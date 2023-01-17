select
        date_trunc('d', _AIRBYTE_EMITTED_AT) as date,
        count(*) num_actions
from {{ source("slack_snowflake", "channel_messages") }}
where date_trunc('d', _AIRBYTE_EMITTED_AT) >= '2022-01-01'
group by 1 order by 1 desc