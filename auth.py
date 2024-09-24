from quart import Blueprint, request, render_template, redirect, url_for
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

@auth.route('/auth/telegram', methods=['GET'])
async def telegram_auth():
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
