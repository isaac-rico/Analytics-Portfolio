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
                    count(*) as edit_count,
                    count(distinct username) as unique_editors,
                    sum(bytes_changed) as total_bytes_changed,
                    avg(bytes_changed) as avg_bytes_changed,
                    min(time_utc) as first_edit,
                    max(time_utc) as last_edit,
                    now() as time_computed
                FROM wiki_edits 
                where time_received > now() - interval '10 minutes'
                and time_received <= now() - interval '5 minutes'
                group by title
                order by time_computed desc
            ),

            curr_window as (
                SELECT
                    title,   
                    count(*) as edit_count,
                    count(distinct username) as unique_editors,
                    sum(bytes_changed) as total_bytes_changed,
                    avg(bytes_changed) as avg_bytes_changed,
                    min(time_utc) as first_edit,
                    max(time_utc) as last_edit,
                    now() as time_computed
                FROM wiki_edits 
                where time_received > now() - interval '5 minutes'
                group by title
                order by time_computed desc
            ),

            velocity as (
                SELECT 
                    curr_window.title,
                    curr_window.edit_count - coalesce(prev_window.edit_count, 0) as velocity, -- velocity as taking the diff between current and previous time windows
                    case
                        when curr_window.edit_count > coalesce(prev_window.edit_count, 0) then 'trending'     -- more activity than prev time window
                        when curr_window.edit_count < coalesce(prev_window.edit_count, 0) then 'not trending' -- less activity than prev time window
                        else 'stable' -- same activity in both time windows
                    end as trend
                FROM curr_window
                left join prev_window on curr_window.title = prev_window.title
            )

            SELECT
                curr_window.title,
                curr_window.edit_count,
                curr_window.unique_editors,
                curr_window.total_bytes_changed,
                curr_window.avg_bytes_changed,
                v.velocity,
                v.trend,
                curr_window.first_edit,
                curr_window.last_edit,
                now() as time_computed
            FROM curr_window 
            left join velocity v on curr_window.title = v.title
            
-- another thing to add: time gap == last edit - first edit

-- stats query

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
where time_utc > now() - interval '1 minute'
group by title, wiki
order by edit_count desc;


-- to open postgres in docker terminal:
-- docker exec -it <db-container-name> psql -U <username> -d <db-name>

-- queries i ran to monitor the data in docker terminal
-- in separate terminals:
select count(*) from wiki_edits;\watch 60 -- refresh every minute
select count(*) from trending_topics;\watch 60 -- refresh every minute

-- for velo stats
select title, unique_editors, edit_count, velocity, trend, first_edit, last_edit, time_computed from trending_topics order by velocity desc limit 20;\watch 300 -- every 5 mins