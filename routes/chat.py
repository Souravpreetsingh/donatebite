from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services import SupabaseService

chat_bp = Blueprint('chat', __name__)

active_calls = {}

@chat_bp.route('/chat')
@login_required
def conversations():
    try:
        convos = SupabaseService.get_conversations(current_user.id)
        return render_template('chat.html', conversations=convos, active_conversation=None, messages=[], other_user=None)
    except Exception as e:
        flash(f'Error loading conversations: {str(e)}', 'danger')
        return render_template('chat.html', conversations=[], active_conversation=None, messages=[], other_user=None)

@chat_bp.route('/chat/<int:donation_id>')
@login_required
def conversation(donation_id):
    try:
        donation = SupabaseService.get_donation_by_id(donation_id)
        if not donation:
            flash('Donation not found.', 'danger')
            return redirect(url_for('chat.conversations'))

        if current_user.id != donation['donor_id']:
            requests = SupabaseService.get_requests_by_donation(donation_id)
            ngo_ids = [r['ngo_id'] for r in requests if r['request_status'] in ('accepted', 'in_transit', 'delivered')]
            if current_user.id not in ngo_ids:
                flash('Access denied.', 'danger')
                return redirect(url_for('chat.conversations'))

        messages = SupabaseService.get_messages(donation_id)
        convos = SupabaseService.get_conversations(current_user.id)

        other_user = None
        if current_user.id == donation['donor_id']:
            requests = SupabaseService.get_requests_by_donation(donation_id)
            for r in requests:
                if r['request_status'] in ('accepted', 'in_transit', 'delivered'):
                    other_user = SupabaseService.get_user_by_id(r['ngo_id'])
                    break
        else:
            other_user = SupabaseService.get_user_by_id(donation['donor_id'])

        return render_template('chat.html',
                               conversations=convos,
                               active_conversation=donation,
                               messages=messages,
                               other_user=other_user)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('chat.conversations'))

@chat_bp.route('/chat/<int:donation_id>/send', methods=['POST'])
@login_required
def send_message(donation_id):
    message = request.form.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        donation = SupabaseService.get_donation_by_id(donation_id)
        if not donation:
            return jsonify({'error': 'Donation not found'}), 404

        if current_user.id == donation['donor_id']:
            requests = SupabaseService.get_requests_by_donation(donation_id)
            receiver_id = None
            for r in requests:
                if r['request_status'] in ('accepted', 'in_transit', 'delivered'):
                    receiver_id = r['ngo_id']
                    break
        else:
            receiver_id = donation['donor_id']

        if not receiver_id:
            return jsonify({'error': 'No conversation partner available'}), 400

        msg = SupabaseService.create_message(
            donation_id=donation_id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=message
        )
        return jsonify({'success': True, 'message': msg}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/<int:donation_id>/messages')
@login_required
def get_messages(donation_id):
    try:
        messages = SupabaseService.get_messages(donation_id)
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/call/<int:donation_id>/start', methods=['POST'])
@login_required
def start_call(donation_id):
    data = request.get_json()
    peer_id = data.get('peer_id')
    if not peer_id:
        return jsonify({'error': 'peer_id required'}), 400
    active_calls[donation_id] = {
        'caller_id': current_user.id,
        'peer_id': peer_id,
    }
    return jsonify({'success': True})

@chat_bp.route('/call/<int:donation_id>/check')
@login_required
def check_call(donation_id):
    call = active_calls.get(donation_id)
    if call and call['caller_id'] != current_user.id:
        return jsonify({'active': True, 'peer_id': call['peer_id']})
    return jsonify({'active': False})

@chat_bp.route('/call/<int:donation_id>/end', methods=['POST'])
@login_required
def end_call(donation_id):
    active_calls.pop(donation_id, None)
    return jsonify({'success': True})
