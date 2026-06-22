"""
CREATE TABLE users (
    id            BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    full_name     TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password      TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('donor', 'ngo', 'admin')),
    phone_number  TEXT DEFAULT '',
    address       TEXT DEFAULT '',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
"""
