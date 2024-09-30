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

# ... (rest of the code remains the same until the update_dutch_auctions function)

async def update_dutch_auctions():
    try:
        current_time = datetime.utcnow()
        dutch_auctions = db_session.query(Auction).filter(
            Auction.is_active == True,
            Auction.auction_type == AuctionType.DUTCH
        ).all()

        for auction in dutch_auctions:
            time_elapsed = (current_time - auction.end_time).total_seconds()
            intervals_passed = int(time_elapsed / auction.dutch_interval)
            new_price = max(0, auction.starting_price - (intervals_passed * auction.dutch_price_decrement))
            
            if new_price <= 0:
                auction.is_active = False
                logger.info(f"Dutch auction {auction.id} ended without a winner")
            else:
                auction.current_dutch_price = new_price

        db_session.commit()
        logger.info("Successfully updated Dutch auctions")
    except Exception as e:
        logger.error(f"Error updating Dutch auctions: {str(e)}")
        db_session.rollback()
    finally:
        db_session.close()

# ... (rest of the code remains the same)

if __name__ == '__main__':
    asyncio.run(main())
