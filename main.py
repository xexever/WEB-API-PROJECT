from flask import Flask, render_template, redirect, request, make_response, jsonify, url_for
from data.users import User
from data.news import News
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.NewsForm import NewsForm
from forms.ProfileForm import ProfileForm, PasswordChangeForm
from flask_login import LoginManager, current_user
from flask_login import login_user, login_required, logout_user
from data import db_session
from flask_restful import Api
from data import news_api
import os
from werkzeug.utils import secure_filename
from PIL import Image

# Создаем приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# Конфигурация для загрузки файлов (ПОСЛЕ создания app)
UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# Создаем папку для аватаров, если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Инициализация API
api = Api(app)

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def allowed_file(filename):
    """Проверка разрешенных расширений файлов"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_avatar(avatar_file, user_id):
    """Сохранение аватара с изменением размера"""
    if avatar_file and allowed_file(avatar_file.filename):
        # Создаем безопасное имя файла
        ext = avatar_file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"user_{user_id}_{os.urandom(8).hex()}.{ext}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            # Открываем и обрабатываем изображение
            img = Image.open(avatar_file)

            # Изменяем размер до 200x200 (сохраняя пропорции)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # Создаем квадратное изображение (центрируем)
            new_img = Image.new('RGB', (200, 200), (255, 255, 255))
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Вставляем изображение по центру
            x = (200 - img.size[0]) // 2
            y = (200 - img.size[1]) // 2
            new_img.paste(img, (x, y))

            # Сохраняем
            new_img.save(filepath, optimize=True, quality=85)

            return f'/static/uploads/avatars/{filename}'
        except Exception as e:
            print(f"Ошибка при сохранении аватара: {e}")
            return None
    return None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        # Создаем пользователя
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)

        # Сначала сохраняем пользователя, чтобы получить его ID
        db_sess.add(user)
        db_sess.commit()

        # Сохраняем аватар если он был загружен
        if form.avatar.data:
            avatar_path = save_avatar(form.avatar.data, user.id)
            if avatar_path:
                user.avatar = avatar_path
                db_sess.commit()

        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile/<int:user_id>')
def profile(user_id):
    """Страница профиля пользователя"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user:
        abort(404)

    # Проверяем, может ли текущий пользователь редактировать этот профиль
    can_edit = current_user.is_authenticated and current_user.id == user_id

    return render_template('profile.html', user=user, can_edit=can_edit)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Редактирование профиля"""
    form = ProfileForm()

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if request.method == "GET":
        # Заполняем форму текущими данными
        form.name.data = user.name
        form.email.data = user.email
        form.about.data = user.about

    if form.validate_on_submit():
        # Обновляем только те поля, которые были изменены
        if form.name.data and form.name.data != user.name:
            user.name = form.name.data

        if form.email.data and form.email.data != user.email:
            # Проверяем, не занят ли email другим пользователем
            existing_user = db_sess.query(User).filter(User.email == form.email.data).first()
            if existing_user and existing_user.id != user.id:
                return render_template('edit_profile.html',
                                       form=form,
                                       user=user,
                                       message="Этот email уже используется другим пользователем")
            user.email = form.email.data

        if form.about.data != user.about:
            user.about = form.about.data

        # Обработка нового аватара
        if form.avatar.data:
            avatar_path = save_avatar(form.avatar.data, user.id)
            if avatar_path:
                # Удаляем старый аватар, если это не дефолтный
                if user.avatar and user.avatar != '/static/default_avatar.png':
                    old_avatar_path = os.path.join(app.root_path, user.avatar[1:])
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                user.avatar = avatar_path

        db_sess.commit()
        return redirect(url_for('profile', user_id=user.id))

    return render_template('edit_profile.html', form=form, user=user)


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Смена пароля"""
    form = PasswordChangeForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if form.validate_on_submit():
        # Проверяем текущий пароль
        if user.check_password(form.current_password.data):
            # Устанавливаем новый пароль
            user.set_password(form.new_password.data)
            db_sess.commit()
            return jsonify({'success': True, 'message': 'Пароль успешно изменен!'})
        else:
            return jsonify({'success': False, 'message': 'Неверный текущий пароль'}), 400

    errors = {}
    for field, field_errors in form.errors.items():
        errors[field] = field_errors
    return jsonify({'success': False, 'errors': errors}), 400


@app.route('/delete_avatar', methods=['POST'])
@login_required
def delete_avatar():
    """Удаление аватара"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if user.avatar and user.avatar != '/static/default_avatar.png':
        # Удаляем файл
        avatar_path = os.path.join(app.root_path, user.avatar[1:])
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

        # Устанавливаем аватар по умолчанию
        user.avatar = '/static/default_avatar.png'
        db_sess.commit()
        return jsonify({'success': True, 'message': 'Аватар удален'})

    return jsonify({'success': False, 'message': 'Аватар не найден'}), 400


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/blogs.db")
    api.add_resource(news_api.NewsListResource, '/api/v2/news')
    api.add_resource(news_api.NewsResource, '/api/v2/news/<int:news_id>')
    app.run(debug=True)


if __name__ == '__main__':
    main()