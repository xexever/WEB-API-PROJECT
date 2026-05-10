from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[
        DataRequired(message="Email обязателен"),
        Email(message="Некорректный email адрес")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Пароль обязателен"),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    password_again = PasswordField('Повторите пароль', validators=[
        DataRequired(message="Подтверждение пароля обязательно"),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    name = StringField('Имя пользователя', validators=[
        DataRequired(message="Имя пользователя обязательно"),
        Length(min=2, max=50, message="Имя должно быть от 2 до 50 символов")
    ])
    about = TextAreaField("Немного о себе")
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только изображения!')
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', field.data):
            raise ValidationError('Введите корректный email адрес')