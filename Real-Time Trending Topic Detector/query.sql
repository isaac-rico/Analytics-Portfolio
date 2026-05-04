
-- trending

SELECT 
    title,   
    wiki,
    count(*) as edit_count,
    count(distinct username) as unique_editors,
    min(time_utc) as first_edit,
    max(time_utc) as last_edit
FROM wiki_edits 
where time_utc > DATEADD(minute, -5, GETDATE())
group by title, wiki
order by edit_count desc;

-- editor count

SELECT count(distinct username) FROM wiki_edits
where time_utc > DATEADD(minute, -5, GETDATE())
group by title
order by count(distinct username) desc;

