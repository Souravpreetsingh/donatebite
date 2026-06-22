-- ─────────────────────────────────────────────────────────────
-- Nourish Collective — Complete Supabase Schema
-- Run this entire script in the Supabase SQL Editor.
-- ─────────────────────────────────────────────────────────────

-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id            BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    full_name     TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password      TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('donor', 'ngo', 'admin')),
    phone_number  TEXT DEFAULT '',
    address       TEXT DEFAULT '',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Donations
CREATE TABLE IF NOT EXISTS donations (
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

-- 3. Donation Requests
CREATE TABLE IF NOT EXISTS donation_requests (
    id               BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id      BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    ngo_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_status   TEXT DEFAULT 'pending'
                     CHECK (request_status IN ('pending','accepted','in_transit','delivered','cancelled')),
    request_date     TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id          BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Messages (Chat)
CREATE TABLE IF NOT EXISTS messages (
    id            BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id   BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    sender_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id   BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message       TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_donation ON messages(donation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);

-- 6. Admin Logs
CREATE TABLE IF NOT EXISTS admin_logs (
    id           BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    admin_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action       TEXT NOT NULL,
    action_time  TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────
-- Seed Data: Default Admin Account (optional)
-- Password: admin123
--
-- Generate the hash in Python first:
--   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('admin123'))"
-- Then copy the output into the INSERT below.
-- ─────────────────────────────────────────────────────────────
-- INSERT INTO users (full_name, email, password, role)
-- VALUES ('Admin', 'admin@nourish.com', '<paste-hash-here>', 'admin');
