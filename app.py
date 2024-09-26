import os
import logging
import time
from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, abort
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import User, Auction
from auth import auth
from admin import admin
from telegram_bot import setup_bot
from db import db_session, init_db, get_db_connection
from forms import AuctionForm
import asyncio
from datetime import datetime
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config.from_object(Config)

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Инициализация Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(User, int(user_id))

# Регистрация Blueprint'ов
app.register_blueprint(auth)
app.register_blueprint(admin)

# Инициализация базы данных
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/active_auctions')
def get_active_auctions():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            engine = get_db_connection()
            with engine.connect() as connection:
                query = db_session.query(Auction).filter_by(is_active=True)
                logging.info(f"SQL Query: {query}")
                active_auctions = query.all()
                logging.info(f"Active auctions: {active_auctions}")

                result = []
                for auction in active_auctions:
                    logging.info(f"Processing auction: {auction}, Type: {type(auction)}")
                    if isinstance(auction, Auction):
                        end_time = auction.end_time
                        if isinstance(end_time, datetime):
                            end_time = end_time.isoformat()
                        else:
                            end_time = str(end_time)
                        
                        auction_data = {
                            'id': auction.id,
                            'title': auction.title,
                            'current_price': auction.current_price,
                            'end_time': end_time
                        }
                    else:
                        logging.warning(f"Unexpected auction type: {type(auction)}")
                        auction_data = {'error': 'Unknown auction type'}

                    result.append(auction_data)

                return jsonify(result)
        except OperationalError as e:
            logging.error(f"Database connection error (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                return jsonify({'error': 'Database connection error'}), 500
            time.sleep(2 ** attempt)  # Exponential backoff

@app.route('/watchlist')
@login_required
def watchlist():
    return render_template('watchlist.html', auctions=current_user.watchlist)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/add_to_watchlist/<int:auction_id>', methods=['POST'])
@login_required
def add_to_watchlist(auction_id):
    auction = db_session.get(Auction, auction_id)
    if auction and auction not in current_user.watchlist:
        current_user.watchlist.append(auction)
        db_session.commit()
    return redirect(url_for('auction_detail', auction_id=auction_id))

@app.route('/remove_from_watchlist/<int:auction_id>', methods=['POST'])
@login_required
def remove_from_watchlist(auction_id):
    auction = db_session.get(Auction, auction_id)
    if auction and auction in current_user.watchlist:
        current_user.watchlist.remove(auction)
        db_session.commit()
    return redirect(url_for('watchlist'))

@app.route('/create_auction', methods=['GET', 'POST'])
@login_required
def create_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        new_auction = Auction(
            title=form.title.data,
            description=form.description.data,
            current_price=form.starting_price.data,
            end_time=form.end_time.data,  # This is already a datetime object
            is_active=True,
            creator=current_user
        )
        db_session.add(new_auction)
        db_session.commit()
        flash('Your auction has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_auction.html', title='Create Auction', form=form)

@app.route('/auction/<int:auction_id>')
def auction_detail(auction_id):
    auction = db_session.get(Auction, auction_id)
    if auction is None:
        abort(404)
    return render_template('auction_detail.html', auction=auction)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('errors/500.html'), 500

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

async def run_app():
    config = HyperConfig()
    config.bind = [f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"]
    config.use_reloader = False
    await serve(app, config)

async def run_bot(application):
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def main():
    bot_application = setup_bot()
    app_task = asyncio.create_task(run_app())
    bot_task = asyncio.create_task(run_bot(bot_application))

    try:
        await asyncio.gather(app_task, bot_task)
    except asyncio.CancelledError:
        logging.info("Tasks were cancelled")
    except Exception as e:
        logging.error(f"Error in main function: {e}")
    finally:
        if hasattr(bot_application, 'is_initialized') and bot_application.is_initialized():
            await bot_application.stop()
            await bot_application.shutdown()
        logging.info("Application shutdown complete")

if __name__ == '__main__':
    asyncio.run(main())
