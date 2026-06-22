-- ─────────────────────────────────────────────────────────────
-- Nourish Collective — Clean Supabase Schema
-- Run this ONCE in the Supabase SQL Editor to reset and
-- create all tables.  No sample data — starts empty.
-- ─────────────────────────────────────────────────────────────

-- ═════════════════════════════════════════════════════════════
--  DROP existing tables (clean slate)
-- ═════════════════════════════════════════════════════════════
DROP TABLE IF EXISTS admin_logs         CASCADE;
DROP TABLE IF EXISTS messages           CASCADE;
DROP TABLE IF EXISTS notifications      CASCADE;
DROP TABLE IF EXISTS donation_requests  CASCADE;
DROP TABLE IF EXISTS donations          CASCADE;
DROP TABLE IF EXISTS users              CASCADE;

-- ═════════════════════════════════════════════════════════════
-- 1.  USERS
-- ═════════════════════════════════════════════════════════════
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

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role  ON users(role);

-- ═════════════════════════════════════════════════════════════
-- 2.  DONATIONS
-- ═════════════════════════════════════════════════════════════
CREATE TABLE donations (
    id                BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donor_id          BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_name         TEXT NOT NULL,
    food_type         TEXT NOT NULL CHECK (food_type IN ('produce','bakery','prepared','dairy','dry')),
    quantity          TEXT NOT NULL,
    preparation_time  TIMESTAMPTZ,
    expiry_time       TIMESTAMPTZ NOT NULL,
    pickup_location   TEXT NOT NULL,
    notes             TEXT DEFAULT '',
    image_url         TEXT DEFAULT '',
    status            TEXT DEFAULT 'available'
                      CHECK (status IN ('available','accepted','in_transit','delivered','cancelled')),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_donations_donor_id   ON donations(donor_id);
CREATE INDEX IF NOT EXISTS idx_donations_status     ON donations(status);
CREATE INDEX IF NOT EXISTS idx_donations_created_at ON donations(created_at DESC);

-- ═════════════════════════════════════════════════════════════
-- 3.  DONATION REQUESTS
-- ═════════════════════════════════════════════════════════════
CREATE TABLE donation_requests (
    id               BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id      BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    ngo_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_status   TEXT DEFAULT 'pending'
                     CHECK (request_status IN ('pending','accepted','in_transit','delivered','cancelled')),
    request_date     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_requests_donation_id ON donation_requests(donation_id);
CREATE INDEX IF NOT EXISTS idx_requests_ngo_id      ON donation_requests(ngo_id);
CREATE INDEX IF NOT EXISTS idx_requests_status      ON donation_requests(request_status);

-- ═════════════════════════════════════════════════════════════
-- 4.  NOTIFICATIONS
-- ═════════════════════════════════════════════════════════════
CREATE TABLE notifications (
    id          BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id   ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread    ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);

-- ═════════════════════════════════════════════════════════════
-- 5.  MESSAGES (Chat)
-- ═════════════════════════════════════════════════════════════
CREATE TABLE messages (
    id            BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id   BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    sender_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id   BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message       TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_donation ON messages(donation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender   ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);

-- ═════════════════════════════════════════════════════════════
-- 6.  ADMIN LOGS
-- ═════════════════════════════════════════════════════════════
CREATE TABLE admin_logs (
    id           BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    admin_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action       TEXT NOT NULL,
    action_time  TIMESTAMPTZ DEFAULT NOW()
);

-- ═════════════════════════════════════════════════════════════
-- 7.  ACTIVE CALLS (ephemeral; used for WebRTC signaling)
-- ═════════════════════════════════════════════════════════════
CREATE TABLE active_calls (
    id            BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id   BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    caller_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    peer_id       TEXT NOT NULL,
    started_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_active_calls_donation ON active_calls(donation_id);

CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_time     ON admin_logs(action_time DESC);

-- ═════════════════════════════════════════════════════════════
-- REFRESH SUPABASE SCHEMA CACHE
-- ═════════════════════════════════════════════════════════════
SELECT pg_catalog.pg_sleep(0.1);
NOTIFY pgrst, 'reload schema';

-- ═════════════════════════════════════════════════════════════
-- VERIFICATION
-- ═════════════════════════════════════════════════════════════
-- Run this separately to confirm:
-- SELECT 'users' AS tbl, count(*) FROM users
-- UNION ALL SELECT 'donations', count(*) FROM donations
-- UNION ALL SELECT 'donation_requests', count(*) FROM donation_requests
-- UNION ALL SELECT 'notifications', count(*) FROM notifications
-- UNION ALL SELECT 'messages', count(*) FROM messages
-- UNION ALL SELECT 'admin_logs', count(*) FROM admin_logs;
