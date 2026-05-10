from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email  # ✅ Добавить Email

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[
        DataRequired(message="Введите email"),
        Email(message="Некорректный формат email")
    ])
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль")])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')