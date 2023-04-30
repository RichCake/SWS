from flask import Flask, render_template, redirect, request, make_response, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User
from data.posts import News
from data.likes import Like
from data.forms import RegisterForm, LoginForm, NewsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    def sort_by_likes_dislikes(news):
        likes_dislikes = []
        for new in news:
            likes = db_sess.query(Like).filter(Like.post_id == new.id, Like.is_like == True).count()
            dislikes = db_sess.query(Like).filter(Like.post_id == new.id, Like.is_like == False).count()
            likes_dislikes.append(likes - dislikes)
        return [new for _, new in sorted(zip(likes_dislikes, news), reverse=True)]

    news = sort_by_likes_dislikes(news)
    return render_template("index.html", news=news)


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
        if form.image.data:
            print(form.image)
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


@app.route('/like/<int:id>', methods=['GET', 'POST'])
@login_required
def like(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()

    if news:
        like = db_sess.query(Like).filter(Like.user_id == current_user.id,
                                          Like.post_id == id).first()

        if like:
            if like.is_like:
                db_sess.delete(like)
                db_sess.commit()
                return redirect('/')
            else:
                like.is_like = True
                db_sess.commit()
                return redirect('/')
        else:
            new_like = Like(user_id=current_user.id,
                            post_id=id,
                            is_like=True)
            db_sess.add(new_like)
            db_sess.commit()
            return redirect('/')
    else:
        abort(404)
    return redirect('/')


@app.route('/dislike/<int:id>', methods=['GET', 'POST'])
@login_required
def dislike(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()

    if news:
        like = db_sess.query(Like).filter(Like.user_id == current_user.id,
                                          Like.post_id == id).first()

        if like:
            if not like.is_like:
                db_sess.delete(like)
                db_sess.commit()
                return redirect('/')
            else:
                like.is_like = False
                db_sess.commit()
                return redirect('/')
        else:
            new_like = Like(user_id=current_user.id,
                            post_id=id,
                            is_like=False)
            db_sess.add(new_like)
            db_sess.commit()
            return redirect('/')
    else:
        abort(404)
    return redirect('/')


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


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/social.db")
    app.run()


if __name__ == '__main__':
    main()
