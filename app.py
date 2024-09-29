import os
import logging
from flask import Flask, render_template, redirect, url_for, jsonify, request, flash, abort
from flask_login import LoginManager, login_required, current_user
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
    filename='app.py',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

bot_application = None

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

# ... [rest of the existing routes]

if __name__ == '__main__':
    bot_application = setup_bot()  # Remove the 'app' argument
    app.run(host='0.0.0.0', port=5000, debug=True)
