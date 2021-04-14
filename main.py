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
from data.comments import Comment
from data.likes import ArticleLike
from forms.user import RegisterForm, LoginForm, EditUserForm
from forms.article import ArticleForm
from forms.comment import CommentForm
from model_workers.user import UserModelWorker
from model_workers.article import ArticleModelWorker
from model_workers.comment import CommentModelWorker
from model_workers.article_like import ArticleLikeModelWorker
from tools.errors import PasswordMismatchError, EmailAlreadyUseError, \
    UserAlreadyExistError, IncorrectPasswordError, ArticleNotFoundError, LikeAlreadyThereError
from parsers.redirect_url import parser as redirect_url_parser

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
        try:
            UserModelWorker.new_user({
                "name": form.name.data,
                "surname": form.surname.data,
                "nickname": form.nickname.data,
                "email": form.email.data,
                "password": form.password.data,
                "password_again": form.password_again.data,
                "description": form.description.data,
                "avatar": form.avatar.data
            })
        except PasswordMismatchError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароли не совпадают",
                                   message_class="alert-danger")
        except EmailAlreadyUseError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Почта уже используется",
                                   message_class="alert-danger")
        except UserAlreadyExistError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   message_class="alert-danger")
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
        try:
            UserModelWorker.edit_user(user.id, {
                "name": form.name.data,
                "surname": form.surname.data,
                "nickname": form.nickname.data,
                "email": form.email.data,
                "description": form.description.data,
                "avatar": form.avatar.data,
                "password": form.password.data,
                "new_password": form.new_password.data,
                "new_password_again": form.new_password_again.data
            })
        except IncorrectPasswordError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Неверный пароль",
                                   message_class="alert-danger")
        except UserAlreadyExistError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   message_class="alert-danger")
        except EmailAlreadyUseError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Почта уже используется",
                                   message_class="alert-danger")
        except PasswordMismatchError:
            return render_template(template_name,
                                   title=title,
                                   form=form,
                                   message="Пароли не совпадают",
                                   message_class="alert-danger")
        return redirect(f"/user_page/{user.id}")
    return render_template(template_name, title=title, form=form)


@app.route("/user_page/<int:user_id>")
@app.route("/user_page/<int:user_id>/page<int:page_index>")
def user_page(user_id, page_index=1):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    articles_count = 10
    user_articles_count = len(user.articles)
    max_page_index = max((user_articles_count // articles_count +
                          (0 if user_articles_count % articles_count == 0 else 1)), 1)
    if page_index > max_page_index:
        abort(404)
    articles = sorted(user.articles, key=lambda x: x.create_date, reverse=True)[
               (page_index - 1) * articles_count:page_index * articles_count
               ]
    return render_template("user_page.html", title=f"@{user.nickname}", user=user,
                           articles_list=articles, page_index=page_index,
                           max_page_index=max_page_index)


@app.route("/article", methods=["GET", "POST"])
@login_required
def add_article():
    template_name = "add_article.html"
    title = "Добавить статью"
    form = ArticleForm()
    if form.validate_on_submit():
        ArticleModelWorker.new_article({
            "title": form.title.data,
            "content": form.content.data,
            "author": current_user.id,
            "image": form.image.data
        })
        return redirect(f"/user_page/{current_user.id}")
    return render_template(template_name, title=title, form=form)


@app.route("/edit_article/<int:article_id>", methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    template_name = "add_article.html"
    title = "Редактировать статью"
    form = ArticleForm()
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        abort(404)
    if article.user != current_user:
        abort(403)
    if request.method == "GET":
        form.title.data = article.title
        form.content.data = article.content
    if form.validate_on_submit():
        try:
            ArticleModelWorker.edit_article(article_id, {
                "title": form.title.data,
                "content": form.content.data,
                "image": form.image.data
            })
        except ArticleNotFoundError:
            abort(404)
        return redirect(f"/#articleCard{article.id}")
    return render_template(template_name, title=title, form=form)


@app.route("/delete_article/<int:article_id>", methods=["GET", "POST"])
@login_required
def delete_article(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        abort(404)
    if article.user != current_user:
        abort(403)
    ArticleModelWorker.delete_article(article_id)
    return redirect("/")


@app.route("/article/<int:article_id>", methods=["GET", "POST"])
def article_page(article_id):
    form = CommentForm()
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        abort(404)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            abort(401)
        CommentModelWorker.new_comment({
                "text": form.text.data,
                "image": form.image.data,
                "article_id": article_id,
                "author": current_user.id
            })
        form.text.data = None
        form.image.data = None
        return redirect(f"/article/{article_id}#commentForm")
    return render_template("article_page.html", title=article.title,
                           article=article, form=form)


@app.route("/delete_comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if not comment:
        abort(404)
    if comment.user != current_user:
        abort(403)
    article_id = comment.article_id
    CommentModelWorker.delete_comment(comment_id)
    return redirect(f"/article/{article_id}")


@app.route("/like/<int:article_id>")
@login_required
def new_like(article_id):
    args = redirect_url_parser.parse_args()
    try:
        ArticleLikeModelWorker.new_like({
            "article_id": article_id,
            "user_id": current_user.id
        })
    except ArticleNotFoundError:
        abort(404)
    except LikeAlreadyThereError:
        ArticleLikeModelWorker.delete_like({
            "article_id": article_id,
            "user_id": current_user.id
        })
    return redirect(args["redirect_url"])


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
    return render_template("index.html", title="Главная", articles_list=articles,
                           page_index=page_index, max_page_index=max_page_index)


@app.errorhandler(401)
def unauthorized(error):
    return make_response(
        render_template("unauthorized.html", title="Недоступно неавторизованным пользователям"),
        401
    )


@app.errorhandler(403)
def forbidden(error):
    return make_response(
        render_template("forbidden.html", title="Запрещенно"),
        403
    )


@app.errorhandler(404)
def page_not_found(error):
    return make_response(
        render_template("page_not_found.html", title="Страница не найдена"),
        404
    )


if __name__ == '__main__':
    db_session.global_init("db/articles.db")
    app.run()
