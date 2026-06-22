from .supabase_service import SupabaseService


class UserProxy:
    def __init__(self, data):
        self.id = data['id']
        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False
        self.role = data['role']
        self.full_name = data['full_name']
        self.email = data['email']

    def get_id(self):
        return str(self.id)

    def is_donor(self):
        return self.role == 'donor'

    def is_ngo(self):
        return self.role == 'ngo'

    def is_admin(self):
        return self.role == 'admin'
