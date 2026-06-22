"""
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
"""
