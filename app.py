from quart import Quart
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from config import Config
from models import db, User, Auction
from auth import auth
from admin import admin
from telegram_bot import setup_bot, send_notification
import asyncio

app = Quart(__name__)
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
async def index():
    return await app.send_static_file('index.html')

@app.route('/api/active_auctions')
async def get_active_auctions():
    active_auctions = await Auction.query.filter_by(is_active=True).all()
    return [{
        'id': auction.id,
        'title': auction.title,
        'current_price': auction.current_price,
        'end_time': auction.end_time.isoformat()
    } for auction in active_auctions]

@app.route('/watchlist')
@login_required
async def watchlist():
    return await app.render_template('watchlist.html', auctions=current_user.watchlist)

@app.route('/add_to_watchlist/<int:auction_id>', methods=['POST'])
@login_required
async def add_to_watchlist(auction_id):
    auction = await Auction.query.get_or_404(auction_id)
    if auction not in current_user.watchlist:
        current_user.watchlist.append(auction)
        await db.session.commit()
        # Flash message functionality might need to be adjusted for Quart
    return redirect(url_for('auction_detail', auction_id=auction_id))

@app.route('/remove_from_watchlist/<int:auction_id>', methods=['POST'])
@login_required
async def remove_from_watchlist(auction_id):
    auction = await Auction.query.get_or_404(auction_id)
    if auction in current_user.watchlist:
        current_user.watchlist.remove(auction)
        await db.session.commit()
        # Flash message functionality might need to be adjusted for Quart
    return redirect(url_for('watchlist'))

@app.errorhandler(404)
async def not_found_error(error):
    return await app.render_template('errors/404.html'), 404

@app.errorhandler(500)
async def internal_error(error):
    db.session.rollback()
    return await app.render_template('errors/500.html'), 500

async def run_bot(application):
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def main():
    bot_application = setup_bot(app)
    bot_task = asyncio.create_task(run_bot(bot_application))
    config = HyperConfig()
    config.bind = ['0.0.0.0:5000']
    await serve(app, config)
    await bot_task

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    asyncio.run(main())
