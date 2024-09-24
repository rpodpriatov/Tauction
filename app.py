from quart import Quart, render_template, redirect, url_for, jsonify
from quart_auth import QuartAuth, AuthUser, login_required, current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from config import Config
from models import User, Auction, Base
from auth import auth
from admin import admin
from telegram_bot import setup_bot, send_notification
from db import engine, async_session  # Import from db.py
import asyncio
import os

app = Quart(__name__)
app.config.from_object(Config)

print(f"Telegram Bot Username: {os.environ.get('TELEGRAM_BOT_USERNAME')}")  # Added print statement

auth_manager = QuartAuth(app)

app.register_blueprint(auth)
app.register_blueprint(admin)

@app.before_serving
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/api/active_auctions')
async def get_active_auctions():
    async with async_session() as session:
        result = await session.execute(select(Auction).filter_by(is_active=True))
        active_auctions = result.scalars().all()
        return jsonify([{
            'id': auction.id,
            'title': auction.title,
            'current_price': auction.current_price,
            'end_time': auction.end_time.isoformat()
        } for auction in active_auctions])

@app.route('/watchlist')
@login_required
async def watchlist():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == int(current_user.auth_id)))
        user = result.scalar_one_or_none()
        if user:
            await session.refresh(user)
            return await render_template('watchlist.html', auctions=user.watchlist)
        return 'User not found', 404

@app.route('/add_to_watchlist/<int:auction_id>', methods=['POST'])
@login_required
async def add_to_watchlist(auction_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == int(current_user.auth_id)))
        user = result.scalar_one_or_none()
        if user:
            auction = await session.get(Auction, auction_id)
            if auction and auction not in user.watchlist:
                user.watchlist.append(auction)
                await session.commit()
            return redirect(url_for('auction_detail', auction_id=auction_id))
        return 'User not found', 404

@app.route('/remove_from_watchlist/<int:auction_id>', methods=['POST'])
@login_required
async def remove_from_watchlist(auction_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == int(current_user.auth_id)))
        user = result.scalar_one_or_none()
        if user:
            auction = await session.get(Auction, auction_id)
            if auction and auction in user.watchlist:
                user.watchlist.remove(auction)
                await session.commit()
            return redirect(url_for('watchlist'))
        return 'User not found', 404

@app.errorhandler(404)
async def not_found_error(error):
    return await render_template('errors/404.html'), 404

@app.errorhandler(500)
async def internal_error(error):
    async with async_session() as session:
        await session.rollback()
    return await render_template('errors/500.html'), 500

async def run_bot(application):
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def main():
    bot_application = setup_bot(app)

    config = HyperConfig()
    config.bind = ['0.0.0.0:5000']

    bot_task = asyncio.create_task(run_bot(bot_application))
    web_task = asyncio.create_task(serve(app, config))

    try:
        await asyncio.gather(bot_task, web_task)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await bot_application.stop()
        await bot_application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
