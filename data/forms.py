from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    image = FileField('Картинка', validators=[FileAllowed(['jpg', 'png'])])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')