# Deployment Guide — Nourish Collective

**Architecture:**
- **Frontend** → Netlify or Vercel (static HTML + Bootstrap + JS)
- **Backend** → Render (Flask + Gunicorn)
- **Database** → Supabase PostgreSQL
- **Storage** → Supabase Storage (`food-images` bucket)

---

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a free project.
2. In the **SQL Editor**, run the schema below to create all tables:

```sql
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
    status            TEXT DEFAULT 'available' CHECK (status IN ('available','accepted','in_transit','delivered','cancelled')),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE donation_requests (
    id               BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    donation_id      BIGINT NOT NULL REFERENCES donations(id) ON DELETE CASCADE,
    ngo_id           BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_status   TEXT DEFAULT 'pending' CHECK (request_status IN ('pending','accepted','in_transit','delivered','cancelled')),
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

-- Optional: seed an admin user (password = hashed "admin123")
-- INSERT INTO users (full_name, email, password, role)
-- VALUES ('Admin', 'admin@nourish.com', '<werkzeug-hash>', 'admin');
```

3. In **Storage**, create a public bucket named `food-images`.
4. In **Project Settings → API**, copy:
   - `Project URL`
   - `anon public key`
   - `service_role key`

---

## Step 2: Prepare the Backend

### 2a. Configure environment

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=food-images
SECRET_KEY=generate-a-random-64-char-string
FLASK_ENV=production
```

### 2b. Test locally

```bash
pip install -r requirements.txt
python app.py
```

Verify: `curl http://127.0.0.1:5000/health`

### 2c. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-org/nourish-collective-backend.git
git push -u origin main
```

> **Important:** Add `.env` to `.gitignore` — never commit secrets.

---

## Step 3: Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Fill in:

   | Field | Value |
   |---|---|
   | Name | `nourish-collective-backend` |
   | Runtime | **Python 3** |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2` |
   | Plan | **Free** |

5. In the **Environment Variables** section, add:

   ```
   SUPABASE_URL=<your-url>
   SUPABASE_KEY=<your-anon-key>
   SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
   SUPABASE_STORAGE_BUCKET=food-images
   SECRET_KEY=<random-64-char-string>
   FLASK_ENV=production
   ```

6. Click **Create Web Service**.

Render will build and deploy. Once done, note the URL:
```
https://nourish-collective-backend.onrender.com
```

---

## Step 4: Deploy Frontend on Netlify

1. Create a separate GitHub repo for the frontend (the `frontend/` folder).

   ```bash
   cd frontend
   git init
   git add .
   git commit -m "Frontend initial"
   git remote add origin https://github.com/your-org/nourish-collective-frontend.git
   git push -u origin main
   ```

2. Go to [netlify.com](https://netlify.com) → **Add new site** → **Import from Git**.
3. Connect your frontend repo.
4. Set:

   | Field | Value |
   |---|---|
   | Build command | *(leave empty — static files)* |
   | Publish directory | `.` (root) |
5. Under **Environment variables**, add:

   ```
   # Not needed at build time — the frontend auto-detects the backend URL in config.js
   ```

6. Click **Deploy**.

7. After deploy, update `frontend/js/config.js` in the backend repo:
   - Change `API_BASE_URL` to `https://nourish-collective-backend.onrender.com`
   - Also update the CORS origins in `app.py` to include your Netlify URL

8. Re-deploy the backend on Render (automatic if connected to GitHub).

---

## Step 4 (Alternative): Deploy Frontend on Vercel

1. Push the `frontend/` folder to a GitHub repo.
2. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**.
3. Import your GitHub repo.
4. Set:

   | Field | Value |
   |---|---|
   | Framework Preset | **Other** |
   | Root Directory | `.` |
   | Build Command | *(leave empty)* |
   | Output Directory | `.` |

5. Deploy. The `vercel.json` file handles client-side routing.

---

## Step 5: Update CORS in Backend

In `app.py`, add your frontend domain to the CORS origins:

```python
CORS(app, supports_credentials=True, origins=[
    'https://nourish-collective.netlify.app',
    'https://nourish-collective.vercel.app',
    # Add your actual deployed URLs here
])
```

Then redeploy the backend (git push triggers auto-deploy on Render).

---

## Step 6: Test the Complete Workflow

| Action | Steps |
|---|---|
| 1. Register a Donor | Open frontend → **Get Started** → Select "Corporate Donor" → Submit |
| 2. Login as Donor | Login with email/password → Redirected to **Donor Dashboard** |
| 3. Add a Donation | Click **Add New Donation** → Fill form → Upload image → Submit |
| 4. Register an NGO | Open in incognito → **Get Started** → Select "Community Partner (NGO)" |
| 5. Login as NGO | Login → **NGO Dashboard** → See available donations |
| 6. Accept Donation | Click **Accept Donation** on a listing → Status changes to "Accepted" |
| 7. Admin Monitoring | Login as `admin@nourish.com` → See users, donations, activity |

---

## Troubleshooting

### CORS errors in browser
```
Access to fetch at 'https://api...' has been blocked by CORS policy
```
**Fix:** Verify the frontend domain is listed in `CORS()` origins in `app.py`. Ensure no trailing slash.

### 401 Unauthorized on every request
**Fix:** The Flask session cookie domain must match. On Render, ensure `SESSION_COOKIE_SAMESITE = 'Lax'` and `SESSION_COOKIE_SECURE = True`.

### Image upload fails
**Fix:** Confirm the `food-images` bucket exists in Supabase Storage and is set to **public**. Check the service role key has storage permissions.

### 500 Internal Server Error
**Fix:** Check Render logs: Dashboard → Your service → **Logs**. Look for Python tracebacks.

### Database queries return empty
**Fix:** Verify tables exist in Supabase SQL Editor. Run `SELECT * FROM users;` to confirm data.

---

## Security Recommendations

1. **Never commit `.env`** — it is in `.gitignore`.
2. Use a **strong random SECRET_KEY** (64+ chars): `python -c "import secrets; print(secrets.token_hex(32))"`.
3. **Restrict Supabase bucket permissions** — set bucket to public only for reads; use service role key for writes from the backend.
4. Enable **Row Level Security (RLS)** in Supabase if you want per-user data isolation (advanced).
5. On Render, enable **Auto-Deploy** only from the main branch.
6. Set **FLASK_ENV=production** to disable debug mode.

---

## Free Hosting Limitations & Solutions

| Service | Limitation | Mitigation |
|---|---|---|
| **Render (Free)** | 750 hours/month, sleeps after 15 min idle | Use a cron-job.org ping every 10 min to keep it awake. |
| **Render (Free)** | 512 MB RAM, 0.1 CPU | Enough for this app; one worker is fine. |
| **Supabase (Free)** | 500 MB DB, 1 GB storage, 2 MB file upload limit | Compress images before upload. Clean old data periodically. |
| **Netlify (Free)** | 300 build minutes/month, 100 GB bandwidth | Static site → near-zero build usage after initial deploy. |
| **Vercel (Free)** | 100 GB bandwidth, 6000 build minutes | Similar — deploy once and it's essentially free. |

**Keep-alive workaround** (Render free tier):

Create a free account at [cron-job.org](https://cron-job.org) and set a job:
- **URL:** `https://nourish-collective-backend.onrender.com/health`
- **Interval:** Every 10 minutes

This prevents the free service from spinning down.

---

## Project Structure (Final)

```
nourish-collective-backend/
├── app.py
├── config.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
├── DEPLOYMENT.md
├── routes/
│   ├── auth.py
│   ├── donor.py
│   ├── ngo.py
│   └── admin.py
├── models/
│   ├── user.py
│   ├── donation.py
│   └── request.py
├── services/
│   └── supabase_service.py
├── templates/
├── static/
└── frontend/          ← Deploy this folder to Netlify/Vercel
    ├── index.html
    ├── login.html
    ├── register.html
    ├── donor-dashboard.html
    ├── ngo-dashboard.html
    ├── admin-dashboard.html
    ├── donate.html
    ├── _redirects
    ├── vercel.json
    ├── css/style.css
    └── js/
        ├── config.js
        └── api.js
```
