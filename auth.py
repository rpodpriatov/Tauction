from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from sqlalchemy import select
from db import db_session
import hmac
import hashlib
from config import Config
import logging

auth = Blueprint('auth', __name__)

logger = logging.getLogger(__name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/auth/telegram', methods=['GET'])
def telegram_auth():
    auth_data = request.args.to_dict()
    if not validate_telegram_auth(auth_data):
        return render_template('login.html', error="Invalid Telegram authentication")

    user_id = auth_data['id']
    username = auth_data.get('username') or f"user_{user_id}"

    user = db_session.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        user = User(telegram_id=user_id, username=username, is_active=True)
        db_session.add(user)
        db_session.commit()
    login_user(user)

    return redirect(url_for('index'))

@auth.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        user_id = current_user.id
        logout_user()
        logger.info(f"User logged out: {user_id}")
    else:
        logger.info("Logout attempted for already logged out user")
    return redirect(url_for('index'))

def validate_telegram_auth(auth_data):
    bot_token = Config.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return False

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    sorted_data = sorted((k, v) for k, v in auth_data.items() if k != 'hash')
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_data)
    hash_digest = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(hash_digest, auth_data['hash'])
