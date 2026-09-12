# Academy Apartments — Flask backend + admin CMS

This replaces the static site with a real Flask app. Your homepage,
apartments page and register form now read from a database, and you can
manage everything (listings + enquiries) from `/admin`.

## What changed from the static version
- `templates/` — same pages as before, now Jinja templates pulling from the database
- `static/` — same CSS/JS/images, unchanged in spirit
- `app.py` — the Flask app: public routes + admin routes
- `db.py` / `models.py` — a plain SQLite database (`academy.db`, created automatically on
  first run) with two tables: `apartments` and `enquiries`. No separate database
  server needed — it's a single file.
- `templates/admin/` — the CMS: login, dashboard, listings manager, enquiries manager

## Setup (one-time)

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and set a real admin password (see the comment inside it for
how to generate the hash). Until you do, the default login is:

- Username: `admin`
- Password: `academy2026`

**Change this before the site is ever public.**

## Running it

```bash
python3 app.py
```

Visit `http://127.0.0.1:5000` for the site, `http://127.0.0.1:5000/admin` for the CMS.

The database and its two starting listings (Studio, One-Bedroom) are created
automatically the first time you run it — nothing to set up by hand.

## Using the admin CMS

- **Dashboard** (`/admin`) — quick counts + your 5 most recent enquiries
- **Listings** (`/admin/apartments`) — add, edit, or delete apartment types.
  Each one needs a unique `slug` (used in the "Register interest" link) and an
  `image_filename` that matches a photo you've uploaded to `static/images/`.
- **Enquiries** (`/admin/enquiries`) — every Register Interest submission
  lands here. Click the status badge to toggle Contacted/New.

Adding a new apartment type (e.g. a "Penthouse") is now just: upload the
photo to `static/images/`, then add it in `/admin/apartments` — no code
changes, no new zip from me needed for that.

## Deploying this for real
This ships with Flask's built-in dev server, which is fine for testing but
says so itself — it's not meant for production traffic. When you're ready to
put this on a real domain, the common next steps are:
- Run it behind a proper WSGI server (e.g. Gunicorn) instead of `python3 app.py`
- Host it somewhere that supports Python (Render, Railway, PythonAnywhere, a VPS, etc.)
- Set `SECRET_KEY` and `ADMIN_PASSWORD_HASH` as real environment variables there,
  not just in a local `.env` file

Happy to help with whichever hosting option you pick when you get there.
