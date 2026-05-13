from flask import Flask, render_template, redirect, request, make_response, jsonify, url_for, abort
from data.users import User
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.ProfileForm import ProfileForm, PasswordChangeForm
from forms.IdeaForm import GenerateIdeaForm
from data.ideas import Idea
from services.api_service import APIService
from flask_login import LoginManager, current_user
from flask_login import login_user, login_required, logout_user
from data import db_session
import os
from werkzeug.utils import secure_filename
from PIL import Image

os.makedirs('db', exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xadktbtidcxrhdbjrwhdcxrpcsbtipaaddzrjitidvtiwtg'

UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_avatar(avatar_file, user_id):
    if avatar_file and allowed_file(avatar_file.filename):
        ext = avatar_file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"user_{user_id}_{os.urandom(8).hex()}.{ext}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            img = Image.open(avatar_file)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            new_img = Image.new('RGB', (200, 200), (255, 255, 255))
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            x = (200 - img.size[0]) // 2
            y = (200 - img.size[1]) // 2
            new_img.paste(img, (x, y))
            new_img.save(filepath, optimize=True, quality=85)
            return f'/static/uploads/avatars/{filename}'
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    return None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        return db_sess.get(User, user_id)
    finally:
        db_sess.close()  # ВАЖНО: закрываем сессию


@app.route("/")
def index():
    """Главная страница"""
    return render_template('index.html', title='FunLearn English')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Passwords do not match")

        db_sess = db_session.create_session()
        try:
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Register',
                                       form=form,
                                       message="User already exists")

            user = User(
                name=form.name.data,
                email=form.email.data,
                about=form.about.data
            )
            user.set_password(form.password.data)

            db_sess.add(user)
            db_sess.commit()

            if form.avatar.data:
                avatar_path = save_avatar(form.avatar.data, user.id)
                if avatar_path:
                    user.avatar = avatar_path
                    db_sess.commit()
        finally:
            db_sess.close()

        return redirect('/login')

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        finally:
            db_sess.close()
        return render_template('login.html',
                               message="Invalid email or password",
                               form=form)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).filter(User.id == user_id).first()
        if not user:
            abort(404)
        can_edit = current_user.is_authenticated and current_user.id == user_id

        user_ideas = db_sess.query(Idea).filter(
            Idea.author_id == user_id,
            Idea.is_published == True
        ).order_by(Idea.created_date.desc()).all()

        user_favorites = user.favorite_ideas

        return render_template('profile.html',
                               user=user,
                               can_edit=can_edit,
                               user_ideas=user_ideas,
                               user_favorites=user_favorites)
    finally:
        db_sess.close()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if request.method == "GET":
            form.name.data = user.name
            form.email.data = user.email
            form.about.data = user.about

        if form.validate_on_submit():
            if form.name.data and form.name.data != user.name:
                user.name = form.name.data
            if form.email.data and form.email.data != user.email:
                existing_user = db_sess.query(User).filter(User.email == form.email.data).first()
                if existing_user and existing_user.id != user.id:
                    return render_template('edit_profile.html', form=form, user=user, message="Email already in use")
                user.email = form.email.data
            if form.about.data != user.about:
                user.about = form.about.data
            if form.avatar.data:
                avatar_path = save_avatar(form.avatar.data, user.id)
                if avatar_path:
                    if user.avatar and user.avatar != '/static/default_avatar.png':
                        old_path = os.path.join(app.root_path, user.avatar[1:])
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    user.avatar = avatar_path
            db_sess.commit()
            return redirect(url_for('profile', user_id=user.id))
    finally:
        db_sess.close()

    return render_template('edit_profile.html', form=form, user=user)


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if form.validate_on_submit():
            if user.check_password(form.current_password.data):
                user.set_password(form.new_password.data)
                db_sess.commit()
                return jsonify({'success': True, 'message': 'Password changed successfully'})
            return jsonify({'success': False, 'message': 'Invalid current password'}), 400

        errors = {field: err for field, err in form.errors.items()}
        return jsonify({'success': False, 'errors': errors}), 400
    finally:
        db_sess.close()


@app.route('/delete_avatar', methods=['POST'])
@login_required
def delete_avatar():
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if user.avatar and user.avatar != '/static/default_avatar.png':
            path = os.path.join(app.root_path, user.avatar[1:])
            if os.path.exists(path):
                os.remove(path)
            user.avatar = '/static/default_avatar.png'
            db_sess.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Avatar not found'}), 400
    finally:
        db_sess.close()


@app.route('/generate_idea', methods=['GET', 'POST'])
@login_required
def generate_idea():
    form = GenerateIdeaForm()

    if request.method == 'POST':
        category = form.category.data
        idea_data = APIService.generate_idea(category)
    else:  # GET request
        idea_data = APIService.generate_idea('random')

    return render_template('generate_idea.html',
                           form=form,
                           idea=idea_data,
                           title='Idea Generator')


@app.route('/save_idea', methods=['POST'])
@login_required
def save_idea():
    data = request.json

    db_sess = db_session.create_session()
    try:
        category = data.get('category', 'random')

        # Формируем полное описание и дополнительные поля в зависимости от категории
        description = data.get('description', '')
        extra_data = {}

        if category == 'joke':
            joke_setup = data.get('joke_setup', '')
            joke_punchline = data.get('joke_punchline', '')
            description = f"Setup: {joke_setup}\nPunchline: {joke_punchline}"
            extra_data['joke'] = f"{joke_setup} - {joke_punchline}"

        elif category == 'trivia':
            question = data.get('description', '')
            correct_answer = data.get('correct_answer', '')
            description = f"Question: {question}\n\nAnswer: {correct_answer}"
            extra_data['correct_answer'] = correct_answer

        elif category == 'name_info':
            name_data = data.get('name_data', {})
            name = name_data.get('name', 'Unknown')
            age = name_data.get('age', 'Unknown')
            gender = name_data.get('gender', 'Unknown')
            country = name_data.get('country', 'Unknown')
            description = f"Name Analysis: {name}\n\n"
            description += f"Estimated age: {age}\n"
            description += f"Gender: {gender}\n"
            description += f"Country: {country}\n"
            description += f"\nBased on statistical data from social networks"
            extra_data['name_data'] = name_data

        elif category == 'food':
            ingredients = data.get('ingredients', '')
            cuisine = data.get('cuisine', '')
            description = f"{data.get('title', 'Delicious Dish')}\n\n"
            if cuisine:
                description += f"Cuisine: {cuisine}\n"
            if ingredients:
                description += f"Ingredients: {ingredients}\n"
            if data.get('extra_info'):
                description += f"\n{data.get('extra_info')}"

        elif category == 'advice':
            description = f"💡 {data.get('description', '')}"
            if data.get('extra_info'):
                description += f"\n\n{data.get('extra_info')}"

        is_published = data.get('is_published', False)

        idea = Idea(
            title=data.get('title', 'New Idea'),
            description=description,
            category=category,
            joke=extra_data.get('joke', data.get('joke', '')),
            image_url='',
            author_id=current_user.id,
            is_published=is_published
        )

        if category == 'trivia' and extra_data.get('correct_answer'):
            idea.description = description
        if category == 'name_info' and extra_data.get('name_data'):
            idea.description = description

        db_sess.add(idea)
        db_sess.commit()
        db_sess.refresh(idea)

        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if not is_published:
            if idea not in user.favorite_ideas:
                user.favorite_ideas.append(idea)
                db_sess.commit()

        return jsonify({
            'success': True,
            'idea_id': idea.id,
            'saved_to_favorites': not is_published,
            'published': is_published
        })
    except Exception as e:
        print(f"Error saving idea: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_sess.close()


@app.route('/add_to_favorites/<int:idea_id>', methods=['POST'])
@login_required
def add_to_favorites(idea_id):
    db_sess = db_session.create_session()
    try:
        idea = db_sess.query(Idea).filter(Idea.id == idea_id).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if idea:
            if idea not in user.favorite_ideas:
                user.favorite_ideas.append(idea)
                db_sess.commit()
                return jsonify({'success': True, 'message': 'Idea added to favorites'})
            else:
                return jsonify({'success': False, 'message': 'Idea already in favorites'}), 400

        return jsonify({'success': False, 'message': 'Idea not found'}), 404
    finally:
        db_sess.close()


@app.route('/my_favorites')
@login_required
def my_favorites():
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template('my_favorites.html',
                               ideas=user.favorite_ideas,
                               title='My Favorites')
    finally:
        db_sess.close()


@app.route('/public_ideas')
@login_required
def public_ideas():
    db_sess = db_session.create_session()
    try:
        ideas = db_sess.query(Idea).filter(Idea.is_published == True).order_by(Idea.created_date.desc()).all()
        return render_template('public_ideas.html', ideas=ideas, title='Community Ideas')
    finally:
        db_sess.close()


@app.route('/my_ideas')
@login_required
def my_ideas():
    db_sess = db_session.create_session()
    try:
        ideas = db_sess.query(Idea).filter(Idea.author_id == current_user.id, Idea.is_published == True).all()
        return render_template('my_ideas.html', ideas=ideas, title='My Ideas')
    finally:
        db_sess.close()


@app.route('/delete_from_favorites/<int:idea_id>', methods=['DELETE'])
@login_required
def delete_from_favorites(idea_id):
    db_sess = db_session.create_session()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        idea = db_sess.query(Idea).filter(Idea.id == idea_id).first()

        if idea and idea in user.favorite_ideas:
            user.favorite_ideas.remove(idea)
            db_sess.commit()
            return jsonify({'success': True, 'message': 'Idea removed from favorites'})

        return jsonify({'success': False, 'message': 'Idea not found in favorites'}), 404
    finally:
        db_sess.close()


@app.route('/delete_my_idea/<int:idea_id>', methods=['DELETE'])
@login_required
def delete_my_idea(idea_id):
    db_sess = db_session.create_session()
    try:
        idea = db_sess.query(Idea).filter(Idea.id == idea_id, Idea.author_id == current_user.id).first()

        if idea:
            for user in idea.favorited_by:
                user.favorite_ideas.remove(idea)
            db_sess.delete(idea)
            db_sess.commit()
            return jsonify({'success': True, 'message': 'Idea deleted successfully'})

        return jsonify({'success': False, 'message': 'Idea not found or you are not the author'}), 404
    finally:
        db_sess.close()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove_session()


def main():
    db_session.global_init("db/blogs.db")
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()