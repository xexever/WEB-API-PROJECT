from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import Optional, Email, Length, EqualTo, DataRequired


class ProfileForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[Optional(), Length(min=2, max=50)])
    email = EmailField('Почта', validators=[Optional(), Email()])
    about = TextAreaField("О себе", validators=[Optional()])
    avatar = FileField('Аватар', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только изображения!')])
    submit = SubmitField('Сохранить изменения')


class PasswordChangeForm(FlaskForm):  # 👈 ЭТОТ КЛАСС ДОЛЖЕН БЫТЬ
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6, message='Пароль должен быть не менее 6 символов')])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('new_password', message='Пароли не совпадают')])
    submit = SubmitField('Сменить пароль')