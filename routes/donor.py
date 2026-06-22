import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services import SupabaseService

donor_bp = Blueprint('donor', __name__)


def donor_required():
    if not current_user.is_donor():
        flash('Donor access required.', 'danger')
        return False
    return True


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


@donor_bp.route('/donor/dashboard')
@login_required
def dashboard():
    if not donor_required():
        return redirect(url_for('auth.home_redirect'))

    try:
        donations = SupabaseService.get_donations_by_donor(current_user.id)

        total_lbs = sum(
            int(''.join(c for c in d['quantity'] if c.isdigit()) or 0)
            for d in donations
        )
        pending_count = sum(1 for d in donations if d['status'] == 'available')
        completed_count = sum(1 for d in donations if d['status'] == 'delivered')

        return render_template('donor_dashboard.html',
                               donations=donations,
                               total_lbs=total_lbs,
                               pending_count=pending_count,
                               completed_count=completed_count)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('donor_dashboard.html', donations=[], total_lbs=0, pending_count=0, completed_count=0)


@donor_bp.route('/donor/add', methods=['GET', 'POST'])
@login_required
def add_donation():
    if not donor_required():
        return redirect(url_for('auth.home_redirect'))

    if request.method == 'POST':
        food_name = request.form.get('food_name', '').strip()
        food_type = request.form.get('food_type', '').strip()
        quantity = request.form.get('quantity', '').strip()
        pickup_location = request.form.get('pickup_location', '').strip()
        expiry_time = request.form.get('expiry_time', '').strip()
        preparation_time = request.form.get('preparation_time', '')
        notes = request.form.get('notes', '')

        if not all([food_name, food_type, quantity, pickup_location, expiry_time]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('add_food.html')

        valid_types = ['produce', 'bakery', 'prepared', 'dairy', 'dry']
        if food_type not in valid_types:
            flash('Invalid food type.', 'danger')
            return render_template('add_food.html')

        image_url = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                safe_name = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{safe_name}"
                file_bytes = file.read()
                try:
                    SupabaseService.upload_file(file_bytes, unique_name, file.content_type or 'image/jpeg')
                    image_url = SupabaseService.get_public_url(unique_name)
                except Exception as e:
                    flash(f'Image upload failed: {str(e)}', 'warning')

        try:
            SupabaseService.create_donation(
                donor_id=current_user.id,
                food_name=food_name,
                food_type=food_type,
                quantity=quantity,
                prep_time=preparation_time or None,
                expiry_time=expiry_time,
                pickup_loc=pickup_location,
                notes=notes,
                image_url=image_url,
            )

            SupabaseService.create_notification(
                user_id=current_user.id,
                title='Donation Added',
                message=f'Your donation "{food_name}" has been listed successfully.',
            )

            flash('Donation added successfully!', 'success')
            return redirect(url_for('donor.dashboard'))
        except Exception as e:
            flash(f'Failed to add donation: {str(e)}', 'danger')

    return render_template('add_food.html')


@donor_bp.route('/donor/history')
@login_required
def history():
    if not donor_required():
        return redirect(url_for('auth.home_redirect'))
    try:
        donations = SupabaseService.get_donations_by_donor(current_user.id)
        return render_template('donor_dashboard.html', donations=donations, history_view=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('donor.dashboard'))
