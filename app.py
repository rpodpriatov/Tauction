import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from config import Config
from models import User, Auction, Subscriber, Bid, AuctionType
from auth import auth
from admin import admin
from telegram_bot import setup_bot, send_notification
from db import db_session, init_db, engine
from forms import AuctionForm, BidForm
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

migrate = Migrate(app, db_session)

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

@app.route('/create_auction', methods=['GET', 'POST'])
@login_required
def create_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        auction_type = AuctionType[form.auction_type.data]
        new_auction = Auction(
            title=form.title.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            current_price=form.starting_price.data,
            end_time=form.end_time.data,
            is_active=True,
            creator=current_user,
            auction_type=auction_type
        )
        
        if auction_type == AuctionType.DUTCH:
            new_auction.current_dutch_price = form.starting_price.data
            new_auction.dutch_price_decrement = form.dutch_price_decrement.data
            new_auction.dutch_interval = form.dutch_interval.data
        elif auction_type == AuctionType.EVERLASTING:
            new_auction.end_time = datetime.utcnow() + timedelta(years=100)  # Set a very far future date
        
        db_session.add(new_auction)
        db_session.commit()
        flash('Your auction has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_auction.html', title='Create Auction', form=form)

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

            if auction.auction_type == AuctionType.DUTCH:
                if bid_amount != auction.current_dutch_price:
                    flash('For Dutch auctions, you must accept the current price.', 'danger')
                else:
                    # End the auction immediately for Dutch auctions
                    auction.is_active = False
                    auction.current_price = bid_amount
                    new_bid = Bid(amount=bid_amount, bidder=user, auction=auction)
                    db_session.add(new_bid)
                    db_session.commit()
                    flash('Congratulations! You won the Dutch auction!', 'success')
            elif auction.auction_type == AuctionType.CLOSED:
                # For closed auctions, we don't update the current price
                if bid_amount <= auction.starting_price:
                    flash('Your bid must be higher than the starting price.', 'danger')
                elif user.xtr_balance < bid_amount:
                    flash('You don\'t have enough XTR for this bid.', 'danger')
                else:
                    new_bid = Bid(amount=bid_amount, bidder=user, auction=auction)
                    db_session.add(new_bid)
                    db_session.commit()
                    flash('Your bid has been placed successfully!', 'success')
            else:  # English and Everlasting auctions
                if bid_amount <= auction.current_price:
                    flash('Your bid must be higher than the current price.', 'danger')
                elif user.xtr_balance < bid_amount:
                    flash('You don\'t have enough XTR for this bid.', 'danger')
                else:
                    auction.current_price = bid_amount
                    new_bid = Bid(amount=bid_amount, bidder=user, auction=auction)
                    db_session.add(new_bid)
                    db_session.commit()
                    flash('Your bid has been successfully placed!', 'success')

            return redirect(url_for('auction_detail', auction_id=auction_id))

    bids = db_session.query(Bid).filter_by(auction_id=auction_id).order_by(Bid.amount.desc()).all()

    return render_template('auction_detail.html',
                           auction=auction,
                           bids=bids,
                           bid_form=bid_form)

@app.route('/api/auction/<int:auction_id>/bids')
def get_auction_bids(auction_id):
    auction = Auction.query.filter_by(id=auction_id).first()
    if auction is None:
        return jsonify({'error': 'Auction not found'}), 404
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
            if auction.auction_type == AuctionType.EVERLASTING:
                continue  # Skip everlasting auctions

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

async def update_dutch_auctions():
    current_time = datetime.utcnow()
    dutch_auctions = db_session.query(Auction).filter(
        Auction.is_active == True,
        Auction.auction_type == AuctionType.DUTCH
    ).all()

    for auction in dutch_auctions:
        time_elapsed = (current_time - auction.end_time).total_seconds()
        intervals_passed = int(time_elapsed / auction.dutch_interval)
        new_price = auction.starting_price - (intervals_passed * auction.dutch_price_decrement)
        
        if new_price <= 0:
            auction.is_active = False
            logger.info(f"Dutch auction {auction.id} ended without a winner")
        else:
            auction.current_dutch_price = new_price

    db_session.commit()

async def main():
    bot_application = setup_bot()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(close_auctions, 'interval', minutes=1)
    scheduler.add_job(update_dutch_auctions, 'interval', seconds=10)  # Update Dutch auctions every 10 seconds
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