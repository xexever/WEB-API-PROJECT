from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import Optional


class GenerateIdeaForm(FlaskForm):
    category = SelectField('Категория', choices=[
        ('food', '🍕 Что приготовить'),
        ('joke', '😂 Посмеяться'),
        ('random', '🎲 Случайная идея')
    ], validators=[Optional()])
    submit = SubmitField('Сгенерировать ✨')