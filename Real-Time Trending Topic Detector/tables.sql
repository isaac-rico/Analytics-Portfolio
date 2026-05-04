-- SQL script to create the wiki_edits table

CREATE TABLE IF NOT EXISTS wiki_edits (
    id SERIAL primary key, -- id
    title text, -- title
    username text, -- user
    wiki text, -- wiki
    server_url text, -- server_url
    edit_type text, -- type
    bot boolean, -- bot
    bytes_changed int,
    time_utc timestamp, -- timestamp
    time_received timestamp default now()
);

CREATE TABLE IF NOT EXISTS trending_topics (
    id SERIAL primary key,
    title text unique,
    wiki text unique,
    edit_count int,
    unique_editors int,
    total_bytes_changed int,
    avg_bytes_changed int,
    velocity int,
    first_edit timestamp,
    last_edit timestamp,
    time_computed timestamp default now()
);