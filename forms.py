from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class AuctionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    starting_price = IntegerField('Starting Price', validators=[DataRequired(), NumberRange(min=1)])
    end_time = DateTimeField('End Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Create Auction')

class BidForm(FlaskForm):
    amount = IntegerField('Bid Amount', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Place Bid')
