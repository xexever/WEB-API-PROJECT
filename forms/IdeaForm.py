from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import Optional, Length


class GenerateIdeaForm(FlaskForm):
    category = SelectField('Категория', choices=[
        ('activity', 'Чем заняться'),
        ('food', 'Что съесть'),
        ('movie', 'Какой фильм посмотреть'),
        ('place', 'Куда сходить'),
        ('joke', 'Над чем посмеяться'),
        ('random', 'Случайная идея')
    ], validators=[Optional()])
    submit = SubmitField('Сгенерировать идею ✨')