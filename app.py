import os
import logging
from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, abort, session
from config import Config
from models import User, Auction, Subscriber, Bid
from auth import auth
from admin import admin
from telegram_bot import setup_bot, send_notification
from db import db_session, init_db, get_db_connection
from forms import AuctionForm, BidForm
from datetime import datetime, timedelta
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, or_

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.register_blueprint(auth)
app.register_blueprint(admin)

with app.app_context():
    init_db()

@app.route('/')
def index():
    active_auctions = Auction.query.filter_by(is_active=True).order_by(Auction.end_time.asc()).all()
    return render_template('index.html', active_auctions=active_auctions)

# ... [rest of the existing routes]

if __name__ == '__main__':
    bot_application = setup_bot()
    app.run(host='0.0.0.0', port=5000, debug=True)
