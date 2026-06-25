<div align="center">
  <h1>🍽️ DonateBite</h1>
  <p><strong>Connecting surplus food to those in need — one donation at a time.</strong></p>
  <p>
    <a href="https://donatebite.vercel.app">Live Demo</a> ·
    <a href="#features">Features</a> ·
    <a href="#tech-stack">Tech Stack</a> ·
    <a href="#getting-started">Getting Started</a> ·
    <a href="#deployment">Deployment</a>
  </p>
</div>

---

## About

**DonateBite** is a full-stack food donation and redistribution platform that connects businesses with surplus food to local NGOs and community partners. Our mission is to reduce food waste and fight hunger by streamlining the logistics of food recovery — from donation listing, to claiming, to eventual delivery.

---

## Features

### For Donors (Restaurants, Groceries, Caterers)
- Dashboard with donation stats (total lbs donated, pending/completed counts)
- Easy donation listing with food type, quantity, expiry, and pickup location
- Interactive map for pickup location selection (with geolocation & reverse geocoding)
- Image upload for donation items
- Real-time chat with NGOs on accepted donations
- WebRTC voice calling for coordination

### For NGOs (Community Partners)
- Browse available food donations in card grid view
- Interactive Leaflet map showing all available donations
- Accept donations with a single click
- Dashboard with request history and stats
- Real-time chat with donors
- In-app notifications for donation updates

### For Admins
- Platform-wide analytics (total users, donations, requests)
- Manage users, donations, and platform directory
- Activity logging for all admin actions
- Role-based access control

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Tailwind CSS, JavaScript, Leaflet.js, PeerJS |
| **Backend** | Python, Flask, Flask-Login, Flask-CORS |
| **Database** | PostgreSQL (via Supabase) |
| **Auth** | Session-based with Supabase Auth |
| **Storage** | Supabase Storage (food images) |
| **Map Tiles** | OpenStreetMap / Nominatim |
| **Voice Calls** | WebRTC via PeerJS |
| **Deployment** | Vercel (frontend), Render (backend) |

---

## Getting Started

### Prerequisites
- Python 3.14+
- Node.js (for Vercel CLI)
- Supabase account

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/Souravpreetsingh/donatebite.git
cd donatebite

# Set up Python environment
cd Food-Donation-System
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run locally
python app.py
```

### Frontend Setup

The frontend is static HTML. Simply open any `.html` file in your browser or serve with:

```bash
# Using Vercel CLI
vercel dev
```

---

## Project Structure

```
├── index.html                  # Landing page
├── donate.html                 # Donation form
├── login.html                  # Login page
├── register.html               # Registration page
├── donor-dashboard.html        # Donor dashboard
├── ngo-dashboard.html          # NGO dashboard
├── admin-dashboard.html        # Admin dashboard
├── analytics.html              # Platform analytics
├── inventory.html              # Public inventory
├── js/
│   ├── config.js               # API base URL config
│   └── api.js                  # API client & utilities
└── Food-Donation-System/       # Python Flask backend
    ├── app.py                  # Flask application
    ├── config.py               # Configuration
    ├── requirements.txt        # Python dependencies
    ├── Procfile                # Render deployment config
    ├── routes/                 # API route handlers
    ├── models/                 # Database models
    ├── services/               # Business logic layer
    ├── database/schema.sql     # PostgreSQL schema
    ├── static/                 # Static assets (CSS, JS)
    └── templates/              # Jinja2 templates
```

---

## Deployment

- **Frontend**: Deployed on **Vercel** at [donatebite.vercel.app](https://donatebite.vercel.app)
- **Backend**: Deployed on **Render** (or as Vercel serverless functions)

Environment variables required:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

---

## License

This project is licensed under the MIT License.
