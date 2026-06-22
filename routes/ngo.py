from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from services import SupabaseService

ngo_bp = Blueprint('ngo', __name__)


@ngo_bp.route('/ngo/dashboard')
@login_required
def dashboard():
    if not current_user.is_ngo():
        flash('NGO access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        requests = SupabaseService.get_requests_by_ngo(current_user.id)

        accepted_count = SupabaseService.count_requests_by_ngo_and_status(current_user.id, 'accepted')
        pending_count = SupabaseService.count_requests_by_ngo_and_status(current_user.id, 'pending')
        delivered_count = SupabaseService.count_requests_by_ngo_and_status(current_user.id, 'delivered')

        enriched = []
        for r in requests:
            donation = SupabaseService.get_donation_by_id(r['donation_id'])
            donor = SupabaseService.get_user_by_id(donation['donor_id']) if donation else None
            enriched.append({
                'request_id': r['id'],
                'request_status': r['request_status'],
                'request_date': r['request_date'],
                'donation': donation,
                'donor_name': donor['full_name'] if donor else 'Unknown',
            })

        return render_template('ngo_dashboard.html',
                               requests=enriched,
                               accepted_count=accepted_count,
                               pending_count=pending_count,
                               delivered_count=delivered_count)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('ngo_dashboard.html', requests=[], accepted_count=0, pending_count=0, delivered_count=0)


@ngo_bp.route('/ngo/available')
@login_required
def available():
    if not current_user.is_ngo():
        flash('NGO access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        donations = SupabaseService.get_available_donations()
        enriched = []
        for d in donations:
            donor = SupabaseService.get_user_by_id(d['donor_id'])
            enriched.append({**d, 'donor_name': donor['full_name'] if donor else 'Unknown'})
        return render_template('ngo_dashboard.html', available_donations=enriched, show_available=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('ngo.dashboard'))


@ngo_bp.route('/ngo/accept/<int:donation_id>', methods=['POST'])
@login_required
def accept(donation_id):
    if not current_user.is_ngo():
        flash('NGO access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    try:
        donation = SupabaseService.get_donation_by_id(donation_id)
        if not donation:
            flash('Donation not found.', 'danger')
            return redirect(url_for('ngo.available'))

        if donation['status'] != 'available':
            flash('This donation is no longer available.', 'warning')
            return redirect(url_for('ngo.available'))

        if donation['donor_id'] == current_user.id:
            flash('You cannot accept your own donation.', 'danger')
            return redirect(url_for('ngo.available'))

        existing = SupabaseService.get_request_by_donation_and_ngo(donation_id, current_user.id)
        if existing:
            flash('You have already requested this donation.', 'warning')
            return redirect(url_for('ngo.available'))

        SupabaseService.create_request(donation_id, current_user.id, 'accepted')
        SupabaseService.update_donation_status(donation_id, 'accepted')

        SupabaseService.create_notification(
            user_id=donation['donor_id'],
            title='Donation Accepted',
            message=f'Your donation "{donation["food_name"]}" has been accepted.',
        )

        flash('Donation accepted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('ngo.dashboard'))


@ngo_bp.route('/ngo/update-status/<int:request_id>/<status>', methods=['POST'])
@login_required
def update_status(request_id, status):
    if not current_user.is_ngo():
        flash('NGO access required.', 'danger')
        return redirect(url_for('auth.home_redirect'))

    valid_statuses = ['in_transit', 'delivered']
    if status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('ngo.dashboard'))

    try:
        SupabaseService.update_request_status(request_id, status)
        flash(f'Status updated to "{status}".', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('ngo.dashboard'))
