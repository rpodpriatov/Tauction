from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import hmac
import hashlib
import time

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/auth/telegram', methods=['POST'])
def telegram_auth():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    telegram_id = data.get('id')
    username = data.get('username')
    auth_date = data.get('auth_date')
    hash = data.get('hash')

    # Verify the authentication data
    data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(data.items()) if k != 'hash'])
    secret_key = hashlib.sha256(Config.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != hash or time.time() - int(auth_date) > 86400:
        return jsonify({'error': 'Invalid authentication'}), 401

    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return jsonify({'success': True, 'redirect': url_for('index')})

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
