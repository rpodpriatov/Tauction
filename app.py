# app.py

import os
import logging
import time
from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, abort
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import User, Auction, Subscriber, Bid
from auth import auth
from admin import admin
from telegram_bot import setup_bot, send_notification
from db import db_session, init_db, get_db_connection
from forms import AuctionForm, BidForm
import asyncio
from datetime import datetime, timedelta
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import hmac
import hashlib

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(User, int(user_id))

app.register_blueprint(auth)
app.register_blueprint(admin)

with app.app_context():
    init_db()

@app.route('/')
def index():
    active_auctions = Auction.query.filter_by(is_active=True).all()
    inactive_auctions = Auction.query.filter_by(is_active=False).all()
    return render_template('index.html',
                           active_auctions=active_auctions,
                           inactive_auctions=inactive_auctions)

@app.route('/api/active_auctions', methods=['GET'])
def get_active_auctions():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            engine = get_db_connection()
            with engine.connect() as connection:
                Session = sessionmaker(bind=engine)
                session = Session()

                query = session.query(Auction).filter_by(is_active=True)
                logging.info(f"SQL Query: {query}")
                active_auctions = query.all()
                logging.info(f"Active auctions: {active_auctions}")

                result = []
                for auction in active_auctions:
                    if isinstance(auction, Auction):
                        end_time = auction.end_time
                        logging.info(
                            f"Initial end_time value: {end_time} (Type: {type(end_time)})"
                        )

                        if isinstance(end_time, datetime):
                            end_time = end_time.isoformat()
                        elif isinstance(end_time, str):
                            logging.info(
                                f"end_time is already a string: {end_time}")
                        elif end_time is not None:
                            try:
                                end_time = str(end_time)
                            except Exception as e:
                                logging.error(
                                    f"Error converting end_time to string: {str(e)}"
                                )
                                end_time = None
                        else:
                            end_time = None

                        auction_data = {
                            'id': auction.id,
                            'title': auction.title,
                            'current_price': auction.current_price,
                            'end_time': end_time
                        }
                    else:
                        logging.warning(
                            f"Unexpected auction type: {type(auction)}")
                        auction_data = {'error': 'Unknown auction type'}

                    result.append(auction_data)

                session.close()

                return jsonify(result)
        except OperationalError as e:
            logging.error(
                f"Database connection error (attempt {attempt + 1}/{max_retries}): {str(e)}"
            )
            if attempt == max_retries - 1:
                return jsonify({'error': 'Database connection error'}), 500
            time.sleep(2**attempt)

@app.route('/api/auction/<int:auction_id>/bids')
def get_auction_bids(auction_id):
    auction = Auction.query.get_or_404(auction_id)
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.timestamp.desc()).limit(10).all()
    
    bid_history_html = render_template('bid_history.html', bids=bids)
    
    return jsonify({
        'current_price': auction.current_price,
        'bid_history_html': bid_history_html
    })

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
        return jsonify({'success': True, 'message': 'Auction added to watchlist.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Auction already in watchlist or does not exist.'}), 400

@app.route('/remove_from_watchlist/<int:auction_id>', methods=['POST'])
@login_required
def remove_from_watchlist(auction_id):
    auction = db_session.get(Auction, auction_id)
    if auction and auction in current_user.watchlist:
        current_user.watchlist.remove(auction)
        db_session.commit()
        return jsonify({'success': True, 'message': 'Auction removed from watchlist.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Auction not found in your watchlist.'}), 404

@app.route('/create_auction', methods=['GET', 'POST'])
@login_required
def create_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        new_auction = Auction(title=form.title.data,
                              description=form.description.data,
                              current_price=form.starting_price.data,
                              end_time=form.end_time.data,
                              is_active=True,
                              creator=current_user)
        db_session.add(new_auction)
        db_session.commit()
        flash('Ваш аукцион создан!', 'success')
        return redirect(url_for('index'))
    return render_template('create_auction.html',
                           title='Создать Аукцион',
                           form=form)

@app.route('/auction/<int:auction_id>', methods=['GET', 'POST'])
def auction_detail(auction_id):
    auction = db_session.get(Auction, auction_id)
    if auction is None:
        abort(404)

    bid_form = BidForm()

    if bid_form.validate_on_submit():
        if not auction.is_active:
            flash('This auction has ended. Bidding is no longer allowed.', 'warning')
        else:
            bid_amount = bid_form.amount.data
            user = current_user

            if not user.is_authenticated:
                flash('Please log in to place a bid.', 'warning')
                return redirect(url_for('auth.login'))

            if bid_amount <= auction.current_price:
                flash('Your bid must be higher than the current price.', 'danger')
            elif user.xtr_balance < bid_amount:
                flash('You don\'t have enough XTR for this bid.', 'danger')
            else:
                try:
                    new_bid = Bid(amount=bid_amount, bidder=user, auction=auction)
                    db_session.add(new_bid)

                    auction.current_price = bid_amount
                    db_session.commit()

                    logger.info(f"New bid placed: User {user.id} bid {bid_amount} on Auction {auction.id}")

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.timestamp.desc()).limit(10).all()
                        bid_history_html = render_template('bid_history.html', bids=bids)
                        return jsonify({'success': True, 'new_price': auction.current_price, 'bid_history_html': bid_history_html})
                    else:
                        flash('Your bid has been successfully placed!', 'success')
                        return redirect(url_for('auction_detail', auction_id=auction_id))
                except Exception as e:
                    db_session.rollback()
                    logger.error(f"Error placing bid: {e}")
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'error': 'An error occurred while placing your bid. Please try again later.'})
                    else:
                        flash('An error occurred while placing your bid. Please try again later.', 'danger')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'error': 'Invalid form data'})

    bids = db_session.query(Bid).filter_by(auction_id=auction_id).order_by(Bid.amount.desc()).all()

    return render_template('auction_detail.html',
                           auction=auction,
                           bids=bids,
                           bid_form=bid_form)

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

@app.route('/yoomoney_ipn', methods=['POST'])
def yoomoney_ipn():
    try:
        data = request.form.to_dict()
        signature = data.pop('sha1_hash', None)

        if not signature:
            logger.error("No signature found in the IPN data")
            return jsonify({'error': 'No signature'}), 400

        sorted_data = sorted(data.items())
        sorted_data_str = '&'.join(f"{k}={v}" for k, v in sorted_data)

        calculated_hash = hmac.new(
            os.getenv('YOOMONEY_SECRET_KEY').encode(),
            sorted_data_str.encode(), hashlib.sha1).hexdigest()

        if calculated_hash != signature:
            logger.error("Invalid signature for YooMoney IPN")
            return jsonify({'error': 'Invalid signature'}), 400

        if data.get('status') != 'success':
            logger.info(
                f"Received non-success payment status: {data.get('status')}")
            return jsonify({'status': 'ignored'}), 200

        user_id = data.get('metadata[user_id]')
        amount = data.get('metadata[amount]')

        if not user_id or not amount:
            logger.error("Missing user_id or amount in metadata")
            return jsonify({'error': 'Missing data'}), 400

        user = db_session.query(User).filter_by(id=int(user_id)).first()
        if not user:
            logger.error(f"User with id {user_id} not found")
            return jsonify({'error': 'User not found'}), 400

        user.xtr_balance += int(amount)
        db_session.commit()

        logger.info(
            f"YooMoney payment processed for user {user.id}, amount {amount} XTR"
        )

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        logger.error(f"Error processing YooMoney IPN: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

async def close_auctions():
    current_time = datetime.utcnow()
    logger.info(f"Running close_auctions at {current_time}")
    try:
        ended_auctions = db_session.query(Auction).filter(
            Auction.end_time <= current_time, Auction.is_active == True).all()

        logger.info(f"Found {len(ended_auctions)} auctions to close")

        if not ended_auctions:
            logger.info("No auctions to close at this time")
            return

        for auction in ended_auctions:
            auction.is_active = False
            logger.info(f"Closing auction {auction.id}: {auction.title}")

            if auction.bids:
                winning_bid = max(auction.bids, key=lambda bid: bid.amount)
                winner = winning_bid.bidder
                await send_notification(
                    winner.telegram_id,
                    f"Congratulations! You won the auction '{auction.title}' with a bid of {winning_bid.amount} XTR."
                )
                await send_notification(
                    auction.creator.telegram_id,
                    f"Your auction '{auction.title}' has ended. Winner: {winner.username} with a bid of {winning_bid.amount} XTR."
                )
            else:
                await send_notification(
                    auction.creator.telegram_id,
                    f"Your auction '{auction.title}' has ended without any bids."
                )

            db_session.commit()
            logger.info(f"Auction {auction.id} closed successfully")

        logger.info(f"Closed {len(ended_auctions)} auctions")

    except Exception as e:
        logger.error(f"Error in close_auctions: {str(e)}")
        db_session.rollback()

async def main():
    bot_application = setup_bot()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(close_auctions, 'interval', minutes=1)
    scheduler.start()

    async def start_bot():
        await bot_application.initialize()
        await bot_application.start()
        await bot_application.updater.start_polling()

    async def start_app():
        config = HyperConfig()
        config.bind = [
            f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"
        ]
        config.use_reloader = False
        await serve(app, config)

    try:
        await asyncio.gather(start_bot(), start_app())
    except asyncio.CancelledError:
        logging.info("Tasks were cancelled")
    except Exception as e:
        logging.error(f"Error in main function: {e}")
    finally:
        await bot_application.shutdown()
        scheduler.shutdown()
        logging.info("Application shutdown complete")

if __name__ == '__main__':
    asyncio.run(main())