from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from services import SupabaseService, UserProxy

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home_redirect'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip()

        if not full_name or not email or not password or not role:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if role not in ('donor', 'ngo'):
            flash('Invalid role selected.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        try:
            if SupabaseService.get_user_by_email(email):
                flash('An account with this email already exists.', 'danger')
                return render_template('register.html')

            SupabaseService.create_user(
                full_name=full_name, email=email,
                password=password, role=role
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home_redirect'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        try:
            user_data = SupabaseService.get_user_by_email(email)
            if not user_data or not SupabaseService.verify_password(user_data, password):
                flash('Invalid email or password.', 'danger')
                return render_template('login.html')

            proxy = UserProxy(user_data)
            login_user(proxy)

            flash(f'Welcome back, {proxy.full_name}!', 'success')
            return redirect(url_for('auth.home_redirect'))
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home_redirect'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/home')
def home_redirect():
    if current_user.is_donor():
        return redirect(url_for('donor.dashboard'))
    elif current_user.is_ngo():
        return redirect(url_for('ngo.dashboard'))
    elif current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/index')
def index():
    return render_template('index.html')
