import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum, Table
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db import Base
from datetime import datetime

class AuctionType(enum.Enum):
    ENGLISH = "English"
    DUTCH = "Dutch"
    CLOSED = "Closed"
    EVERLASTING = "Everlasting"

watchlist = Table('watchlist', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('auction_id', Integer, ForeignKey('auctions.id'))
)

class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    password_hash = Column(String(128))
    telegram_id = Column(String(64), unique=True)
    xtr_balance = Column(Float, default=0.0)
    auctions = relationship('Auction', back_populates='creator')
    bids = relationship('Bid', back_populates='bidder')
    watchlist = relationship('Auction', secondary=watchlist, back_populates='watchers')
    is_active = Column(Boolean, default=True)  # Добавлено поле is_active

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    starting_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship('User', back_populates='auctions')
    bids = relationship('Bid', back_populates='auction')
    watchers = relationship('User', secondary=watchlist, back_populates='watchlist')
    auction_type = Column(Enum(AuctionType), nullable=False)
    current_dutch_price = Column(Float)
    dutch_price_decrement = Column(Float)
    dutch_interval = Column(Integer)  # Interval in seconds

class Bid(Base):
    __tablename__ = 'bids'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    bidder_id = Column(Integer, ForeignKey('users.id'))
    bidder = relationship('User', back_populates='bids')
    auction_id = Column(Integer, ForeignKey('auctions.id'))
    auction = relationship('Auction', back_populates='bids')

class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subscription_end = Column(DateTime)

