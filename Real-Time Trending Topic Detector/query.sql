-- queries to add to aggregate


-- trending

SELECT 
    title,   
    wiki,
    count(*) as edit_count,
    count(distinct username) as unique_editors,
    sum(bytes_changed) as total_bytes_changed,
    avg(bytes_changed) as avg_bytes_changed,
    min(time_utc) as first_edit,
    max(time_utc) as last_edit,
    now() as time_computed
    FROM wiki_edits 
where time_utc > now() - interval '5 minutes'
group by title, wiki
order by edit_count desc;

-- trending velo
-- previous table comparison
-- first, find the edit count from the previous 5 mins, compare it to the current pull edit count
-- if the current pull is larger, then its trending
with prev_window as (
    SELECT
        title,   
        wiki,
        count(*) as edit_count,
        count(distinct username) as unique_editors,
        sum(bytes_changed) as total_bytes_changed,
        avg(bytes_changed) as avg_bytes_changed,
        min(time_utc) as first_edit,
        max(time_utc) as last_edit,
        now() as time_computed
        FROM wiki_edits 
    where time_computed > interval '10 minutes' and time_computed <= now() - interval '5 minutes'
    order by time_computed desc
),
curr_window as (
    SELECT
        title,   
        wiki,
        count(*) as edit_count,
        count(distinct username) as unique_editors,
        sum(bytes_changed) as total_bytes_changed,
        avg(bytes_changed) as avg_bytes_changed,
        min(time_utc) as first_edit,
        max(time_utc) as last_edit,
        now() as time_computed
        FROM wiki_edits 
    where time_computed > now() - interval '5 minutes'
    order by time_computed desc
),
velocity as (
    SELECT 
        curr_window.title,
        curr_window.edit_count - coalesce(prev_window.edit_count, 0) as velocity,
        case
            when curr_window.edit_count > coalesce(prev_window.edit_count, 0) then 'trending'
            else 'not trending'
        end as trend
    FROM curr_window
    left join prev_window on curr_window.title = prev_window.title
)
SELECT
    curr_window.title,
    curr_window.wiki,
    curr_window.edit_count,
    curr_window.unique_editors,
    curr_window.total_bytes_changed,
    curr_window.avg_bytes_changed,
    curr_window.first_edit,
    curr_window.last_edit,
    now() as time_computed,
    v.velocity,
    v.trend
FROM curr_window 
left join velocity v on curr_window.title = v.title 

