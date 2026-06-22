from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from services import SupabaseService

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        total_users = SupabaseService.count_users()
        total_donors = SupabaseService.count_users_by_role('donor')
        total_ngos = SupabaseService.count_users_by_role('ngo')
        total_donations = SupabaseService.count_donations()

        SupabaseService.create_admin_log(current_user.id, 'Viewed admin dashboard')

        return render_template('admin_dashboard.html',
                               total_users=total_users,
                               total_donors=total_donors,
                               total_ngos=total_ngos,
                               total_donations=total_donations)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin_dashboard.html')


@admin_bp.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        users = SupabaseService.get_all_users()
        enriched = []
        for u in users:
            enriched.append({
                **u,
                'donation_count': len(SupabaseService.get_donations_by_donor(u['id'])),
                'request_count': len(SupabaseService.get_requests_by_ngo(u['id'])),
            })
        SupabaseService.create_admin_log(current_user.id, 'Viewed user management')
        return render_template('admin_dashboard.html', users=enriched, show_users=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/donations')
@login_required
def manage_donations():
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        donations = SupabaseService.get_all_donations()
        enriched = []
        for d in donations:
            donor = SupabaseService.get_user_by_id(d['donor_id'])
            enriched.append({**d, 'donor_name': donor['full_name'] if donor else 'Unknown'})
        SupabaseService.create_admin_log(current_user.id, 'Viewed donation management')
        return render_template('admin_dashboard.html', all_donations=enriched, show_donations=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    if user_id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    try:
        user = SupabaseService.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.manage_users'))

        SupabaseService.delete_user(user_id)
        SupabaseService.create_admin_log(current_user.id, f'Deleted user "{user["full_name"]}"')
        flash(f'User {user["full_name"]} deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/logs')
@login_required
def view_logs():
    if not current_user.is_admin():
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        logs = SupabaseService.get_all_admin_logs()
        enriched = []
        for log in logs:
            admin = SupabaseService.get_user_by_id(log['admin_id'])
            enriched.append({**log, 'admin_name': admin['full_name'] if admin else 'Unknown'})
        return render_template('admin_dashboard.html', logs=enriched, show_logs=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))
