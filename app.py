import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import check_password_hash, generate_password_hash

from db import init_db
from models import Apartment, Enquiry, LoginEvent

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
# Bump this string on any visual update (CSS/JS/image change) so browsers and
# any CDN/host caching never serve a stale stylesheet after a redeploy.
ASSET_VERSION = '5'
# The real domain once this is live — used in the sitemap and social share tags.
# Set SITE_URL in your .env once you have a domain (e.g. https://academyapartments.co.uk).
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:5000').rstrip('/')
# Default password is "academy2026". Set ADMIN_PASSWORD_HASH in your .env to change it
# (see README.md for how to generate one) before this goes anywhere public.
ADMIN_PASSWORD_HASH = os.environ.get(
    'ADMIN_PASSWORD_HASH',
    generate_password_hash('academy2026')
)

init_db()


@app.context_processor
def inject_admin_context():
    return {'admin_username': ADMIN_USERNAME, 'site_url': SITE_URL, 'asset_version': ASSET_VERSION}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


# ============================================================
# PUBLIC ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('index.html', preview_listings=Apartment.all()[:2])


@app.route('/apartments')
def apartments():
    return render_template('apartments.html', listings=Apartment.all())


@app.route('/register-interest', methods=['GET', 'POST'])
def register_interest():
    listings = Apartment.all()

    if request.method == 'POST':
        full_name = request.form.get('fullName', '').strip()
        email = request.form.get('email', '').strip()

        errors = {}
        if not full_name:
            errors['fullName'] = 'Please enter your name.'
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            errors['email'] = 'Please enter a valid email.'

        if errors:
            return render_template(
                'register-interest.html',
                listings=listings,
                submitted=False,
                errors=errors,
                form=request.form,
                prefill_type=request.form.get('apartmentType', ''),
            )

        Enquiry.create(
            full_name=full_name,
            email=email,
            phone=request.form.get('phone', '').strip(),
            move_date=request.form.get('moveDate', '').strip(),
            applicant_type=request.form.get('applicantType', 'student'),
            apartment_type=request.form.get('apartmentType', 'unsure'),
            message=request.form.get('message', '').strip(),
        )

        return render_template(
            'register-interest.html',
            listings=listings,
            submitted=True,
            errors={},
            form={},
            prefill_type='',
        )

    return render_template(
        'register-interest.html',
        listings=listings,
        submitted=False,
        errors={},
        form={},
        prefill_type=request.args.get('type', ''),
    )


@app.route('/robots.txt')
def robots_txt():
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin',
        f'Sitemap: {SITE_URL}/sitemap.xml',
    ]
    return Response('\n'.join(lines), mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap_xml():
    pages = [
        {'loc': url_for('index'), 'priority': '1.0'},
        {'loc': url_for('apartments'), 'priority': '0.9'},
        {'loc': url_for('register_interest'), 'priority': '0.8'},
    ]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in pages:
        xml.append(
            f"  <url><loc>{SITE_URL}{page['loc']}</loc>"
            f"<priority>{page['priority']}</priority></url>"
        )
    xml.append('</urlset>')
    return Response('\n'.join(xml), mimetype='application/xml')


# ============================================================
# ADMIN — AUTH
# ============================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        success = username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password)
        LoginEvent.record(username=username or '(blank)', ip_address=request.remote_addr or '', success=success)
        if success:
            session['is_admin'] = True
            return redirect(request.args.get('next') or url_for('admin_dashboard'))
        error = 'Incorrect username or password.'
    return render_template('admin/login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))


# ============================================================
# ADMIN — DASHBOARD
# ============================================================

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template(
        'admin/dashboard.html',
        apartment_count=Apartment.count(),
        enquiry_count=Enquiry.count(),
        new_enquiry_count=Enquiry.count_not_contacted(),
        recent_enquiries=Enquiry.recent(5),
        recent_logins=LoginEvent.recent(8),
        admin_username=ADMIN_USERNAME,
    )


# ============================================================
# ADMIN — APARTMENT LISTINGS (CMS)
# ============================================================

@app.route('/admin/apartments')
@login_required
def admin_apartments():
    return render_template('admin/apartments_list.html', listings=Apartment.all())


@app.route('/admin/apartments/new', methods=['GET', 'POST'])
@login_required
def admin_apartment_new():
    if request.method == 'POST':
        Apartment.create(
            name=request.form.get('name', '').strip(),
            slug=request.form.get('slug', '').strip(),
            description=request.form.get('description', '').strip(),
            features=request.form.get('features', '').strip(),
            image_filename=request.form.get('image_filename', '').strip(),
        )
        flash('Apartment listing added.')
        return redirect(url_for('admin_apartments'))
    return render_template('admin/apartment_form.html', listing=None)


@app.route('/admin/apartments/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_apartment_edit(listing_id):
    listing = Apartment.get(listing_id)
    if listing is None:
        flash('That listing no longer exists.')
        return redirect(url_for('admin_apartments'))

    if request.method == 'POST':
        Apartment.update(
            listing_id,
            name=request.form.get('name', '').strip(),
            slug=request.form.get('slug', '').strip(),
            description=request.form.get('description', '').strip(),
            features=request.form.get('features', '').strip(),
            image_filename=request.form.get('image_filename', '').strip(),
        )
        flash('Apartment listing updated.')
        return redirect(url_for('admin_apartments'))

    return render_template('admin/apartment_form.html', listing=listing)


@app.route('/admin/apartments/<int:listing_id>/delete', methods=['POST'])
@login_required
def admin_apartment_delete(listing_id):
    Apartment.delete(listing_id)
    flash('Apartment listing deleted.')
    return redirect(url_for('admin_apartments'))


# ============================================================
# ADMIN — ENQUIRIES
# ============================================================

@app.route('/admin/enquiries')
@login_required
def admin_enquiries():
    return render_template('admin/enquiries_list.html', entries=Enquiry.all())


@app.route('/admin/enquiries/<int:enquiry_id>/toggle', methods=['POST'])
@login_required
def admin_enquiry_toggle(enquiry_id):
    Enquiry.toggle_contacted(enquiry_id)
    return redirect(url_for('admin_enquiries'))


@app.route('/admin/enquiries/<int:enquiry_id>/delete', methods=['POST'])
@login_required
def admin_enquiry_delete(enquiry_id):
    Enquiry.delete(enquiry_id)
    flash('Enquiry deleted.')
    return redirect(url_for('admin_enquiries'))


if __name__ == '__main__':
    app.run(debug=True)
