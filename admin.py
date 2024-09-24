from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models import User, Auction

admin = Blueprint('admin', __name__)

@admin.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        abort(403)

@admin.route('/admin')
def dashboard():
    return render_template('admin/dashboard.html')

@admin.route('/admin/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/auctions')
def auctions():
    auctions = Auction.query.all()
    return render_template('admin/auctions.html', auctions=auctions)
