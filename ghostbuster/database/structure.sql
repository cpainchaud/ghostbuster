--- SQLITE3 DATABASE STRUCTURE

-- table GhostAgent
CREATE TABLE GhostAgent (
    href TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    stat_total_hits INTEGER DEFAULT 0
);

-- table GhostAgentWaitListEntry
CREATE TABLE GhostAgentWaitListEntry (
    href TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    has_an_agent INTEGER DEFAULT 0,
    stat_total_hits INTEGER DEFAULT 1
);