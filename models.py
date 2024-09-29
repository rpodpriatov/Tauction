from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db import Base
from datetime import datetime

# Define the association table for the many-to-many watchlist relationship
auction_watchlist = Table(
    'auction_watchlist', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('auction_id', Integer, ForeignKey('auctions.id'), primary_key=True)
)

class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(120), unique=True, nullable=False)
    username = Column(String(64), index=True, unique=True, nullable=False)
    xtr_balance = Column(Integer, default=0, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Many-to-many relationship with Auction for watchlist
    watchlist = relationship('Auction', secondary=auction_watchlist, back_populates='watchers')

    # One-to-many relationship with Auction for created auctions
    auctions = relationship('Auction', back_populates='creator')

    # One-to-one relationship with Subscriber
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'), nullable=True)
    subscriber = relationship('Subscriber', back_populates='user', uselist=False)

    # One-to-many relationship with Bid for user bids
    bids = relationship('Bid', back_populates='bidder', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Auction(Base):
    __tablename__ = 'auctions'

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    description = Column(String(500))
    current_price = Column(Float, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Many-to-many relationship with User for watchlist
    watchers = relationship('User', secondary=auction_watchlist, back_populates='watchlist')

    # Many-to-one relationship with User for creator
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    creator = relationship('User', back_populates='auctions')

    # One-to-many relationship with Bid for auction bids
    bids = relationship('Bid', back_populates='auction', order_by="Bid.amount.desc()", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Auction(id={self.id}, title='{self.title}', current_price={self.current_price}, end_time={self.end_time})>"

class Bid(Base):
    __tablename__ = 'bids'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    bidder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=False)

    # Relationships
    bidder = relationship('User', back_populates='bids')
    auction = relationship('Auction', back_populates='bids')

    def __repr__(self):
        return f"<Bid(id={self.id}, amount={self.amount}, bidder_id={self.bidder_id}, auction_id={self.auction_id})>"

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(120), unique=True, nullable=False)
    username = Column(String(64), nullable=False)
    subscription_status = Column(String(50), default='inactive')
    subscription_end = Column(DateTime)

    # One-to-one relationship with User
    user = relationship('User', back_populates='subscriber')

    def __repr__(self):
        return f"<Subscriber(id={self.id}, telegram_id='{self.telegram_id}', username='{self.username}')>"
