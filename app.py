from flask import Flask, render_template, redirect, url_for, jsonify, request, flash
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import User, Auction
from auth import auth
from admin import admin
from telegram_bot import setup_bot
from db import db_session, init_db
from forms import AuctionForm
import logging
import asyncio
import threading
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)

# Initialize database
with app.app_context():
    init_db()

# Setup Telegram bot
bot_application = None

def run_telegram_bot():
    global bot_application
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_application = setup_bot()
        app.logger.info("Telegram bot initialized successfully")
        loop.run_until_complete(bot_application.run_polling())
    except Exception as e:
        app.logger.error(f"Failed to initialize or run Telegram bot: {str(e)}")

# Start Telegram bot in a separate thread
telegram_thread = threading.Thread(target=run_telegram_bot)
telegram_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/active_auctions')
def get_active_auctions():
    active_auctions = Auction.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': auction.id,
        'title': auction.title,
        'current_price': auction.current_price,
        'end_time': auction.end_time.isoformat()
    } for auction in active_auctions])

@app.route('/watchlist')
@login_required
def watchlist():
    return render_template('watchlist.html', auctions=current_user.watchlist)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/add_to_watchlist/<int:auction_id>', methods=['POST'])
@login_required
def add_to_watchlist(auction_id):
    auction = Auction.query.get(auction_id)
    if auction and auction not in current_user.watchlist:
        current_user.watchlist.append(auction)
        db_session.commit()
    return redirect(url_for('auction_detail', auction_id=auction_id))

@app.route('/remove_from_watchlist/<int:auction_id>', methods=['POST'])
@login_required
def remove_from_watchlist(auction_id):
    auction = Auction.query.get(auction_id)
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
            end_time=form.end_time.data,
            is_active=True,
            creator=current_user
        )
        db_session.add(new_auction)
        db_session.commit()
        flash('Your auction has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_auction.html', title='Create Auction', form=form)

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

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
