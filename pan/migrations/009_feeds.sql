-- Pan migration 009: feed intake (PAN-35) -- lab blogs, newsletters, societies, GitHub releases.
-- Items land in pan.frontier_item (source 'rss' or 'github'); this table is the per-feed poll state
-- that makes every poll a conditional GET (ETag / Last-Modified) and makes a dead feed visible.

create table if not exists pan.feed_state (
    feed_id              text primary key,             -- seeds.json feeds[].feed_id
    url                  text not null,
    kind                 text not null,                -- blog | newsletter | society | releases
    final_url            text,                         -- after redirects, as last served
    etag                 text,
    last_modified        text,
    last_status          integer,                      -- HTTP status of the last poll (304 = unchanged)
    last_error           text,
    last_checked_at      timestamptz,
    last_ok_at           timestamptz,                  -- last 200 or 304
    entries_last         integer,                      -- entries in the last 200 body
    consecutive_failures integer not null default 0
);
