# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from db import Base  # Import Base from db.py

# Association table for watchlist (many-to-many between User and Auction)
watchlist_association = Table(
    'watchlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('auction_id', Integer, ForeignKey('auctions.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    telegram_id = Column(String, unique=True, nullable=True)
    xtr_balance = Column(Integer, default=0)

    # Relationship with Auction through watchlist_association
    watchlist = relationship('Auction', secondary=watchlist_association, back_populates='users')
    bids = relationship('Bid', back_populates='user')

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    current_price = Column(Integer, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationship with User through watchlist_association
    users = relationship('User', secondary=watchlist_association, back_populates='watchlist')
    bids = relationship('Bid', back_populates='auction')

class Bid(Base):
    __tablename__ = 'bids'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    user = relationship('User', back_populates='bids')
    auction = relationship('Auction', back_populates='bids')
