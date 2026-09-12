from datetime import datetime
from db import get_db


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


class Apartment:
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.slug = row['slug']
        self.description = row['description']
        self.features = row['features']
        self.image_filename = row['image_filename']
        self.created_at = _parse_dt(row['created_at'])

    @property
    def feature_list(self):
        return [f.strip() for f in self.features.split(',') if f.strip()]

    @staticmethod
    def all():
        conn = get_db()
        rows = conn.execute('SELECT * FROM apartments ORDER BY id').fetchall()
        conn.close()
        return [Apartment(r) for r in rows]

    @staticmethod
    def get(listing_id):
        conn = get_db()
        row = conn.execute('SELECT * FROM apartments WHERE id = ?', (listing_id,)).fetchone()
        conn.close()
        return Apartment(row) if row else None

    @staticmethod
    def count():
        conn = get_db()
        n = conn.execute('SELECT COUNT(*) FROM apartments').fetchone()[0]
        conn.close()
        return n

    @staticmethod
    def create(name, slug, description, features, image_filename):
        conn = get_db()
        conn.execute(
            '''INSERT INTO apartments (name, slug, description, features, image_filename)
               VALUES (?,?,?,?,?)''',
            (name, slug, description, features, image_filename),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(listing_id, name, slug, description, features, image_filename):
        conn = get_db()
        conn.execute(
            '''UPDATE apartments SET name=?, slug=?, description=?, features=?, image_filename=?
               WHERE id=?''',
            (name, slug, description, features, image_filename, listing_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(listing_id):
        conn = get_db()
        conn.execute('DELETE FROM apartments WHERE id = ?', (listing_id,))
        conn.commit()
        conn.close()


class Enquiry:
    def __init__(self, row):
        self.id = row['id']
        self.full_name = row['full_name']
        self.email = row['email']
        self.phone = row['phone']
        self.move_date = row['move_date']
        self.applicant_type = row['applicant_type']
        self.apartment_type = row['apartment_type']
        self.message = row['message']
        self.contacted = bool(row['contacted'])
        self.created_at = _parse_dt(row['created_at'])

    @staticmethod
    def all():
        conn = get_db()
        rows = conn.execute('SELECT * FROM enquiries ORDER BY created_at DESC, id DESC').fetchall()
        conn.close()
        return [Enquiry(r) for r in rows]

    @staticmethod
    def recent(limit=5):
        conn = get_db()
        rows = conn.execute(
            'SELECT * FROM enquiries ORDER BY created_at DESC, id DESC LIMIT ?', (limit,)
        ).fetchall()
        conn.close()
        return [Enquiry(r) for r in rows]

    @staticmethod
    def get(enquiry_id):
        conn = get_db()
        row = conn.execute('SELECT * FROM enquiries WHERE id = ?', (enquiry_id,)).fetchone()
        conn.close()
        return Enquiry(row) if row else None

    @staticmethod
    def count():
        conn = get_db()
        n = conn.execute('SELECT COUNT(*) FROM enquiries').fetchone()[0]
        conn.close()
        return n

    @staticmethod
    def count_not_contacted():
        conn = get_db()
        n = conn.execute('SELECT COUNT(*) FROM enquiries WHERE contacted = 0').fetchone()[0]
        conn.close()
        return n

    @staticmethod
    def create(full_name, email, phone, move_date, applicant_type, apartment_type, message):
        conn = get_db()
        conn.execute(
            '''INSERT INTO enquiries
               (full_name, email, phone, move_date, applicant_type, apartment_type, message)
               VALUES (?,?,?,?,?,?,?)''',
            (full_name, email, phone, move_date, applicant_type, apartment_type, message),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def toggle_contacted(enquiry_id):
        conn = get_db()
        conn.execute('UPDATE enquiries SET contacted = NOT contacted WHERE id = ?', (enquiry_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(enquiry_id):
        conn = get_db()
        conn.execute('DELETE FROM enquiries WHERE id = ?', (enquiry_id,))
        conn.commit()
        conn.close()


class LoginEvent:
    def __init__(self, row):
        self.id = row['id']
        self.username = row['username']
        self.ip_address = row['ip_address']
        self.success = bool(row['success'])
        self.created_at = _parse_dt(row['created_at'])

    @staticmethod
    def record(username, ip_address, success):
        conn = get_db()
        conn.execute(
            'INSERT INTO login_events (username, ip_address, success) VALUES (?,?,?)',
            (username, ip_address, 1 if success else 0),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def recent(limit=8):
        conn = get_db()
        rows = conn.execute(
            'SELECT * FROM login_events ORDER BY created_at DESC, id DESC LIMIT ?', (limit,)
        ).fetchall()
        conn.close()
        return [LoginEvent(r) for r in rows]
