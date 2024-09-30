# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange  # Добавлен импорт NumberRange

class AuctionForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Описание', validators=[Length(max=500)])
    starting_price = FloatField('Начальная Цена', validators=[DataRequired()])
    end_time = DateTimeField(
        'Время окончания',
        format='%Y-%m-%dT%H:%M',  # Формат соответствует datetime-local в HTML5
        validators=[DataRequired()]
    )
    submit = SubmitField('Создать Аукцион')

class BidForm(FlaskForm):
    amount = FloatField(
        'Ваша ставка (XTR)',
        validators=[
            DataRequired(message="Пожалуйста, введите сумму ставки."),
            NumberRange(min=0.01, message="Сумма ставки должна быть больше 0.")
        ]
    )
    submit = SubmitField('Сделать ставку')
