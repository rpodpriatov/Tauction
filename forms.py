from wtforms import StringField, TextAreaField, DecimalField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf import FlaskForm

class AuctionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    starting_price = DecimalField('Starting Price', validators=[DataRequired(), NumberRange(min=0)])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Create Auction')
