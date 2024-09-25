from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, abort
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
from datetime import datetime
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(User, int(user_id))

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(admin)

# Initialize database
with app.app_context():
    init_db()

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
        'end_time': auction.end_time
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
            end_time=datetime.strptime(form.end_time.data, '%Y-%m-%dT%H:%M'),
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
    auction = Auction.query.get(auction_id)
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
    config.bind = ["0.0.0.0:5000"]
    await serve(app, config)

async def main():
    bot_application = setup_bot()
    bot_task = asyncio.create_task(bot_application.start_polling())
    app_task = asyncio.create_task(run_app())
    
    try:
        await asyncio.gather(bot_task, app_task)
    except asyncio.CancelledError:
        pass
    finally:
        await bot_application.stop()
        await bot_application.shutdown()

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
