from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, redirect, request, url_for, make_response, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User
from data.articles import Article
from forms.user import RegisterForm, LoginForm, EditUserForm
from forms.article import ArticleForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "articles_site"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    template_name = "register.html"
    title = "Регистрация"
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароли не совпадают",
                                   message_class="alert-danger")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Почта уже используется",
                                   message_class="alert-danger")
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   message_class="alert-danger")
        user = User(name=form.name.data, surname=form.surname.data,
                    nickname=form.nickname.data, email=form.email.data)
        user.set_password(form.password.data)
        if form.avatar.data:
            image = Image.open(BytesIO(form.avatar.data.read()))
            while True:
                filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
                if not os.path.exists(f"static/img/avatars/{filename}"):
                    break
            image.save(f"static/img/avatars/{filename}")
            user.avatar = filename
        if form.description.data:
            user.description = form.description.data
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template(template_name, title=title, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    template_name = "login.html"
    title = "Авторизация"
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(template_name,
                               form=form,
                               message="Неправильный логин или пароль",
                               message_class="alert-danger")
    return render_template(template_name, title=title, form=form)


@app.route("/edit_user", methods=["GET", "POST"])
@login_required
def edit_user():
    template_name = "edit_user.html"
    title = "Редактировать аккаунт"
    form = EditUserForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    if request.method == "GET":
        form.name.data = user.name
        form.surname.data = user.surname
        form.nickname.data = user.nickname
        form.email.data = user.email
        form.description.data = user.description
    if form.validate_on_submit():
        if not user.check_password(form.password.data):
            return render_template(template_name, title=title, form=form,
                                   message="Неверный пароль", message_class="alert-danger")
        if db_sess.query(User).filter(User.nickname == form.nickname.data,
                                      User.id != user.id).first():
            return render_template(template_name, title=title, form=form,
                                   message="Такой пользователь уже есть",
                                   message_class="alert-danger")
        if db_sess.query(User).filter(User.email == form.email.data, User.id != user.id).first():
            return render_template(template_name, title=title, form=form,
                                   message="Почта уже используется",
                                   message_class="alert-danger")
        if form.new_password.data:
            if form.new_password.data != form.new_password_again.data:
                return render_template(template_name, title=title, form=form,
                                       message="Пароли не совпадают", message_class="alert-danger")
            user.set_password(form.new_password.data)
        user.name = form.name.data
        user.surname = form.surname.data
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.description = form.description.data
        if form.avatar.data:
            image = Image.open(BytesIO(form.avatar.data.read()))
            while True:
                filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
                if not os.path.exists(f"static/img/avatars/{filename}"):
                    break
            os.remove(f"static/img/avatars/{user.avatar}")
            user.avatar = filename
            image.save(f"static/img/avatars/{user.avatar}")
        db_sess.commit()
        return redirect(f"/user_page/{user.id}")
    return render_template(template_name, title=title, form=form)


@app.route("/user_page/<int:user_id>")
def user_page(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    return render_template("user_page.html", title=f"@{user.nickname}", user=user)


@app.route("/article", methods=["GET", "POST"])
@login_required
def add_article():
    template_name = "add_article.html"
    title = "Добавить статью"
    form = ArticleForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        article = Article(
            title=form.title.data,
            content=form.content.data,
            author=current_user.id
        )
        if form.image.data:
            image = Image.open(BytesIO(form.image.data.read()))
            while True:
                filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
                if not os.path.exists(f"static/img/articles_images/{filename}"):
                    break
            image.save(f"static/img/articles_images/{filename}")
            article.image = filename
        db_sess.add(article)
        db_sess.commit()
        return redirect(f"/user_page/{current_user.id}")
    return render_template(template_name, title=title, form=form)


@app.route("/")
@app.route("/page<int:page_index>")
def index(page_index=1):
    db_sess = db_session.create_session()
    response = db_sess.query(Article).order_by(Article.create_date.desc())
    all_articles_count = response.count()
    articles_count = 10
    max_page_index = max((all_articles_count // articles_count +
                          (0 if all_articles_count % articles_count == 0 else 1)), 1)
    if page_index > max_page_index:
        abort(404)
    articles = response.slice((page_index - 1) * articles_count, page_index * articles_count)
    return render_template("index.html", title="main", articles_list=articles,
                           page_index=page_index, max_page_index=max_page_index)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(
        render_template("unauthorized.html", title="Недоступно неавторизованным пользователям"),
        401
    )


@app.errorhandler(404)
def page_not_found(error):
    return make_response(
        render_template("page_not_found.html", title="Страница не найдена"), 404
    )


if __name__ == '__main__':
    db_session.global_init("db/articles.db")
    app.run()
