import os
from datetime import datetime
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


class SupabaseService:
    _client: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            url = current_app.config['SUPABASE_URL']
            key = current_app.config['SUPABASE_SERVICE_ROLE_KEY']
            cls._client = create_client(url, key)
        return cls._client

    # ── Users ────────────────────────────────────────────

    @classmethod
    def create_user(cls, full_name, email, password, role, phone='', address=''):
        client = cls.get_client()
        hashed = generate_password_hash(password)
        now = datetime.utcnow().isoformat()
        data = {
            'full_name': full_name, 'email': email.lower().strip(),
            'password': hashed, 'role': role,
            'phone_number': phone, 'address': address, 'created_at': now,
        }
        result = client.table('users').insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_user_by_email(cls, email):
        client = cls.get_client()
        result = client.table('users').select('*').eq('email', email.lower().strip()).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_user_by_id(cls, user_id):
        client = cls.get_client()
        result = client.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None

    @classmethod
    def verify_password(cls, user, plain_password):
        return check_password_hash(user['password'], plain_password)

    @classmethod
    def get_all_users(cls):
        client = cls.get_client()
        result = client.table('users').select('*').order('created_at', desc=True).execute()
        return result.data

    @classmethod
    def delete_user(cls, user_id):
        client = cls.get_client()
        client.table('users').delete().eq('id', user_id).execute()

    @classmethod
    def count_users(cls):
        c = cls.get_client()
        r = c.table('users').select('id', count='exact').execute()
        return r.count

    @classmethod
    def count_users_by_role(cls, role):
        c = cls.get_client()
        r = c.table('users').select('id', count='exact').eq('role', role).execute()
        return r.count

    # ── Donations ────────────────────────────────────────

    @classmethod
    def create_donation(cls, donor_id, food_name, food_type, quantity,
                        prep_time, expiry_time, pickup_loc, notes='', image_url=''):
        c = cls.get_client()
        now = datetime.utcnow().isoformat()
        data = {
            'donor_id': donor_id, 'food_name': food_name, 'food_type': food_type,
            'quantity': quantity, 'preparation_time': prep_time,
            'expiry_time': expiry_time, 'pickup_location': pickup_loc,
            'notes': notes, 'image_url': image_url,
            'status': 'available', 'created_at': now,
        }
        result = c.table('donations').insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_donation_by_id(cls, donation_id):
        c = cls.get_client()
        r = c.table('donations').select('*').eq('id', donation_id).execute()
        return r.data[0] if r.data else None

    @classmethod
    def get_donations_by_donor(cls, donor_id):
        c = cls.get_client()
        r = c.table('donations').select('*').eq('donor_id', donor_id).order('created_at', desc=True).execute()
        return r.data

    @classmethod
    def get_available_donations(cls):
        c = cls.get_client()
        r = c.table('donations').select('*').eq('status', 'available').order('created_at', desc=True).execute()
        return r.data

    @classmethod
    def get_all_donations(cls):
        c = cls.get_client()
        r = c.table('donations').select('*').order('created_at', desc=True).execute()
        return r.data

    @classmethod
    def update_donation_status(cls, donation_id, status):
        c = cls.get_client()
        r = c.table('donations').update({'status': status}).eq('id', donation_id).execute()
        return r.data[0] if r.data else None

    @classmethod
    def count_donations(cls):
        c = cls.get_client()
        r = c.table('donations').select('id', count='exact').execute()
        return r.count

    # ── Requests ─────────────────────────────────────────

    @classmethod
    def create_request(cls, donation_id, ngo_id, status='pending'):
        c = cls.get_client()
        now = datetime.utcnow().isoformat()
        data = {'donation_id': donation_id, 'ngo_id': ngo_id, 'request_status': status, 'request_date': now}
        r = c.table('donation_requests').insert(data).execute()
        return r.data[0] if r.data else None

    @classmethod
    def get_request_by_donation_and_ngo(cls, donation_id, ngo_id):
        c = cls.get_client()
        r = c.table('donation_requests').select('*').eq('donation_id', donation_id).eq('ngo_id', ngo_id).execute()
        return r.data[0] if r.data else None

    @classmethod
    def get_requests_by_ngo(cls, ngo_id):
        c = cls.get_client()
        r = c.table('donation_requests').select('*').eq('ngo_id', ngo_id).order('request_date', desc=True).execute()
        return r.data

    @classmethod
    def get_requests_by_donation(cls, donation_id):
        c = cls.get_client()
        r = c.table('donation_requests').select('*').eq('donation_id', donation_id).execute()
        return r.data

    @classmethod
    def count_requests(cls):
        c = cls.get_client()
        r = c.table('donation_requests').select('id', count='exact').execute()
        return r.count

    @classmethod
    def count_requests_by_ngo_and_status(cls, ngo_id, status):
        c = cls.get_client()
        r = c.table('donation_requests').select('id', count='exact').eq('ngo_id', ngo_id).eq('request_status', status).execute()
        return r.count

    @classmethod
    def update_request_status(cls, request_id, status):
        c = cls.get_client()
        c.table('donation_requests').update({'request_status': status}).eq('id', request_id).execute()

    # ── Storage ──────────────────────────────────────────

    @classmethod
    def upload_file(cls, file_bytes, file_name, content_type='image/jpeg'):
        c = cls.get_client()
        bucket = current_app.config['SUPABASE_STORAGE_BUCKET']
        return c.storage.from_(bucket).upload(
            path=file_name, file=file_bytes,
            file_options={'content-type': content_type}
        )

    @classmethod
    def get_public_url(cls, file_name):
        bucket = current_app.config['SUPABASE_STORAGE_BUCKET']
        c = cls.get_client()
        return c.storage.from_(bucket).get_public_url(file_name)

    # ── Notifications ────────────────────────────────────

    @classmethod
    def create_notification(cls, user_id, title, message):
        c = cls.get_client()
        now = datetime.utcnow().isoformat()
        data = {'user_id': user_id, 'title': title, 'message': message, 'is_read': False, 'created_at': now}
        r = c.table('notifications').insert(data).execute()
        return r.data[0] if r.data else None

    @classmethod
    def get_notifications_by_user(cls, user_id):
        c = cls.get_client()
        r = c.table('notifications').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return r.data

    @classmethod
    def get_unread_notification_count(cls, user_id):
        c = cls.get_client()
        r = c.table('notifications').select('id', count='exact').eq('user_id', user_id).eq('is_read', False).execute()
        return r.count

    # ── Messages (Chat) ───────────────────────────────────

    @classmethod
    def create_message(cls, donation_id, sender_id, receiver_id, message):
        c = cls.get_client()
        now = datetime.utcnow().isoformat()
        data = {
            'donation_id': donation_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'message': message,
            'created_at': now,
        }
        result = c.table('messages').insert(data).execute()
        return result.data[0] if result.data else None

    @classmethod
    def get_messages(cls, donation_id):
        c = cls.get_client()
        r = c.table('messages').select('*').eq('donation_id', donation_id).order('created_at').execute()
        return r.data

    @classmethod
    def get_conversations(cls, user_id):
        c = cls.get_client()
        r = c.table('messages').select('donation_id').eq('sender_id', user_id).execute()
        sent_ids = set(m['donation_id'] for m in r.data)
        r = c.table('messages').select('donation_id').eq('receiver_id', user_id).execute()
        received_ids = set(m['donation_id'] for m in r.data)
        donation_ids = list(sent_ids | received_ids)

        convos = []
        for did in donation_ids:
            donation = cls.get_donation_by_id(did)
            if not donation:
                continue
            other_id = None
            requests = cls.get_requests_by_donation(did)
            for req in requests:
                if req['request_status'] in ('accepted', 'in_transit', 'delivered'):
                    other_id = req['ngo_id'] if user_id == donation['donor_id'] else donation['donor_id']
                    break
            if not other_id:
                continue
            other_user = cls.get_user_by_id(other_id)
            msgs = cls.get_messages(did)
            last_msg = msgs[-1] if msgs else None
            convos.append({
                'donation_id': did,
                'donation': donation,
                'other_user': other_user,
                'last_message': last_msg['message'] if last_msg else '',
                'last_message_time': last_msg['created_at'] if last_msg else '',
            })

        convos.sort(key=lambda c: c['last_message_time'], reverse=True)
        return convos

    # ── Admin Logs ────────────────────────────────────────

    @classmethod
    def create_admin_log(cls, admin_id, action):
        c = cls.get_client()
        now = datetime.utcnow().isoformat()
        data = {'admin_id': admin_id, 'action': action, 'action_time': now}
        c.table('admin_logs').insert(data).execute()

    @classmethod
    def get_all_admin_logs(cls):
        c = cls.get_client()
        r = c.table('admin_logs').select('*').order('action_time', desc=True).execute()
        return r.data
