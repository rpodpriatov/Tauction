from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db import Base

auction_watchlist = Table('auction_watchlist', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('auction_id', Integer, ForeignKey('auctions.id'))
)

class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(120), unique=True, nullable=False)
    username = Column(String(64), index=True, unique=True)
    xtr_balance = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # Added this line
    watchlist = relationship('Auction', secondary=auction_watchlist, back_populates='watchers')

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    description = Column(String(500))
    current_price = Column(Integer, nullable=False)
    end_time = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True)
    watchers = relationship('User', secondary=auction_watchlist, back_populates='watchlist')
