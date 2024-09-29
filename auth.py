import os
from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from models import User
from db import db_session
import hashlib
import hmac
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@auth.route('/auth/telegram', methods=['GET', 'POST'])
def telegram_auth():
    # Verify the data received from Telegram
    data = request.args if request.method == 'GET' else request.form
    if not data:
        return 'Authentication failed: No data received', 400

    received_hash = data.get('hash')
    auth_date = data.get('auth_date')

    # Check if the auth_date is not older than 1 day
    if int(auth_date) < (datetime.now() - timedelta(days=1)).timestamp():
        return 'Authentication failed: Data is outdated', 400

    # Remove the hash from the data for comparison
    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data.items()) if k != 'hash')

    # Create a secret key by hashing the bot token
    secret_key = hashlib.sha256(os.environ['TELEGRAM_BOT_TOKEN'].encode('utf-8')).digest()

    # Generate a hash of the data for comparison
    generated_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

    if received_hash != generated_hash:
        return 'Authentication failed: Data is not authentic', 400

    # If the data is authentic, proceed with user login or registration
    user = User.query.filter_by(telegram_id=data.get('id')).first()
    if not user:
        user = User(telegram_id=data.get('id'), username=data.get('username'))
        db_session.add(user)
        db_session.commit()

    session['user_id'] = user.id
    return redirect(url_for('index'))
