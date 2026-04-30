-- SQL script to create the wiki_edits table

CREATE TABLE IF NOT EXISTS wiki_edits (
    id SERIAL primary key,
    title text, 
    user text,
    wiki text,
    server_url text,
    bot boolean,
    time_utc timestamp,
    time_received timestamp default now()
);