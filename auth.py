from quart import Blueprint, request, jsonify, render_template, redirect, url_for
from quart_auth import login_user, logout_user, login_required, current_user, AuthUser
from models import User
from sqlalchemy.future import select
from db import async_session
import hmac
import hashlib
import time
from config import Config
import logging

auth = Blueprint('auth', __name__)

logger = logging.getLogger(__name__)

@auth.route('/login')
async def login():
    return await render_template('login.html')

@auth.route('/auth/telegram', methods=['GET', 'POST'])
async def telegram_auth():
    if request.method == 'POST':
        data = await request.json
        if not data:
            logger.warning("Invalid data received in telegram_auth")
            return jsonify({'error': 'Invalid data'}), 400

        telegram_id = data.get('id')
        username = data.get('username')
        auth_date = data.get('auth_date')
        hash = data.get('hash')

        # Verify the authentication data
        data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(data.items()) if k != 'hash'])
        secret_key = hashlib.sha256(Config.TELEGRAM_BOT_TOKEN.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(calculated_hash, hash):
            logger.warning(f"Invalid hash for user {telegram_id}")
            return jsonify({'error': 'Invalid authentication data'}), 401

        if time.time() - int(auth_date) > 86400:
            logger.warning(f"Expired authentication for user {telegram_id}")
            return jsonify({'error': 'Authentication expired'}), 401

        async with async_session() as session:
            result = await session.execute(select(User).filter_by(telegram_id=str(telegram_id)))
            user = result.scalar_one_or_none()
            if not user:
                user = User(telegram_id=str(telegram_id), username=username)
                session.add(user)
                await session.commit()
                logger.info(f"New user created: {telegram_id}")
            else:
                logger.info(f"Existing user logged in: {telegram_id}")

        auth_user = AuthUser(str(user.id))
        login_user(auth_user)
        logger.info(f"User {telegram_id} successfully authenticated")
        return jsonify({'success': True, 'redirect': url_for('index')})
    else:  # GET request
        # Handle GET request (Telegram widget callback)
        auth_data = request.args.to_dict()
        if not validate_telegram_auth(auth_data):
            return await render_template('login.html', error="Invalid Telegram authentication")

        user_id = auth_data['id']
        username = auth_data.get('username') or f"user_{user_id}"

        async with async_session() as session:
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                user = User(telegram_id=user_id, username=username)
                session.add(user)
                await session.commit()
            auth_user = AuthUser(str(user.id))
            login_user(auth_user)

        return redirect(url_for('index'))

@auth.route('/logout')
@login_required
async def logout():
    logout_user()
    logger.info(f"User logged out: {current_user.auth_id}")
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
