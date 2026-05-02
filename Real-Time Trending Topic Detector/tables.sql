-- SQL script to create the wiki_edits table

CREATE TABLE IF NOT EXISTS wiki_edits (
    id SERIAL primary key, -- id
    title text, -- title
    username text, -- user
    wiki text, -- wiki
    server_url text, -- server_url
    edit_type text, -- type
    bot boolean, -- bot
    time_utc timestamp, -- timestamp
    time_received timestamp default now()
);

CREATE TABLE IF NOT EXISTS trending_topics (
    id SERIAL primary key,
    title text,
    wiki text,
    edit_count int,
    unique_editors int,
    window_start timestamp,
    window_end timestamp,
    time_utc timestamp default now()
);