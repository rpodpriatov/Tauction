from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models import db, User, Auction
from auth import auth
from admin import admin
from telegram_bot import setup_bot, send_notification
import asyncio
import threading

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth)
app.register_blueprint(admin)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

def run_bot(application):
    asyncio.run(application.run_polling())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        bot_application = setup_bot(app)
    
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, args=(bot_application,))
    bot_thread.start()
    
    app.run(host='0.0.0.0', port=5000)
