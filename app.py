from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from models import Auction, AuctionType, User
from forms import AuctionForm
from db import db_session
from auth import auth as auth_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register the auth blueprint
app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))

@app.route('/create_auction', methods=['GET', 'POST'])
@login_required
def create_auction():
    form = AuctionForm()
    if form.validate_on_submit():
        new_auction = Auction(
            title=form.title.data,
            description=form.description.data,
            starting_price=form.starting_price.data,
            current_price=form.starting_price.data,
            end_time=form.end_time.data,
            is_active=True,
            creator=current_user,
            auction_type=AuctionType[form.auction_type.data]
        )
        db_session.add(new_auction)
        db_session.commit()
        flash('Your auction has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_auction.html', title='Create Auction', form=form)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
