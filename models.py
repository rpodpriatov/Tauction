import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db import Base

class AuctionType(enum.Enum):
    ENGLISH = "English"
    DUTCH = "Dutch"
    SEALED_BID = "Sealed-bid"
    PERPETUAL = "Perpetual"

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    telegram_id = Column(String(64), unique=True)
    xtr_balance = Column(Float, default=0.0)
    auctions = relationship('Auction', backref='creator', lazy='dynamic')
    bids = relationship('Bid', backref='bidder', lazy='dynamic')
    watchlist = relationship('Auction', secondary='watchlist', backref='watchers')

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    starting_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bids = relationship('Bid', backref='auction', lazy='dynamic')
    auction_type = Column(Enum(AuctionType), nullable=False)

class Bid(Base):
    __tablename__ = 'bids'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    bidder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=False)

class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    subscription_end = Column(DateTime, nullable=False)
    user = relationship('User', backref='subscriber', uselist=False)

watchlist = Base.metadata.tables['watchlist']
