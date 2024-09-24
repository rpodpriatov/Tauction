from models import db, Auction, User
from datetime import datetime

def close_expired_auctions():
    now = datetime.utcnow()
    expired_auctions = Auction.query.filter(Auction.end_time <= now, Auction.is_active == True).all()
    
    for auction in expired_auctions:
        auction.is_active = False
        winning_bid = auction.bids.order_by(Bid.amount.desc()).first()
        
        if winning_bid:
            winner = winning_bid.bidder
            creator = auction.creator
            
            winner.xtr_balance -= winning_bid.amount
            creator.xtr_balance += winning_bid.amount
        
        db.session.commit()

def get_user_auction_history(user_id):
    user = User.query.get(user_id)
    created_auctions = user.auctions.all()
    participated_auctions = Auction.query.join(Bid).filter(Bid.user_id == user_id).all()
    
    return {
        'created': created_auctions,
        'participated': participated_auctions
    }
