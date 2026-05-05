from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import Optional


class GenerateIdeaForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('food', '🍕 What to Cook'),
        ('joke', '😂 Have a Laugh'),
        ('advice', '💡 Get Advice'),
        ('trivia', '❓ Trivia Question'),
        ('name_info', '📊 Name Analysis'),
        ('random', '🎲 Random Idea')
    ], validators=[Optional()])
    submit = SubmitField('Generate ✨')