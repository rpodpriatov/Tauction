from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateTimeField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from models import AuctionType

class AuctionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    starting_price = FloatField('Starting Price', validators=[DataRequired(), NumberRange(min=0)])
    end_time = DateTimeField('End Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    auction_type = SelectField('Auction Type', choices=[(t.name, t.value) for t in AuctionType], validators=[DataRequired()])
    dutch_price_decrement = FloatField('Price Decrement (Dutch)', validators=[NumberRange(min=0)])
    dutch_interval = IntegerField('Interval in seconds (Dutch)', validators=[NumberRange(min=1)])
    submit = SubmitField('Create Auction')

class BidForm(FlaskForm):
    amount = FloatField('Bid Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Place Bid')
