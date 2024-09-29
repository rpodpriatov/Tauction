import os
import logging
import time
import signal
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
from sqlalchemy import desc, or_

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

bot_application = None
scheduler = None

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(User, int(user_id))

app.register_blueprint(auth)
app.register_blueprint(admin)

with app.app_context():
    init_db()

@app.route('/')
def index():
    active_auctions = Auction.query.filter_by(is_active=True).order_by(Auction.end_time.asc()).all()
    return render_template('index.html', active_auctions=active_auctions)

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
                            'description': auction.description,
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

@app.route('/api/ended_auctions', methods=['GET'])
def get_ended_auctions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    search_query = request.args.get('search', '')
    sort_order = request.args.get('sort', 'end_time_desc')

    query = Auction.query.filter_by(is_active=False)

    if search_query:
        query = query.filter(or_(Auction.title.ilike(f'%{search_query}%'),
                                 Auction.description.ilike(f'%{search_query}%')))

    if sort_order == 'end_time_desc':
        query = query.order_by(Auction.end_time.desc())
    elif sort_order == 'end_time_asc':
        query = query.order_by(Auction.end_time.asc())
    elif sort_order == 'price_desc':
        query = query.order_by(Auction.current_price.desc())
    elif sort_order == 'price_asc':
        query = query.order_by(Auction.current_price.asc())

    paginated_auctions = query.paginate(page=page, per_page=per_page, error_out=False)

    auctions_data = []
    for auction in paginated_auctions.items:
        auctions_data.append({
            'id': auction.id,
            'title': auction.title,
            'current_price': auction.current_price,
            'end_time': auction.end_time.isoformat(),
            'winner': auction.winner.username if auction.winner else None
        })

    return jsonify({
        'auctions': auctions_data,
        'total_pages': paginated_auctions.pages,
        'current_page': page
    })

# ... [rest of the file remains unchanged]

