"""
CREATE TABLE donation_requests (
    id               BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id      BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    ngo_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_status   TEXT DEFAULT 'pending'
                     CHECK (request_status IN ('pending','accepted','in_transit','delivered','cancelled')),
    request_date     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE notifications (
    id          BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    message     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE admin_logs (
    id           BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    admin_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action       TEXT NOT NULL,
    action_time  TIMESTAMPTZ DEFAULT NOW()
);
"""
