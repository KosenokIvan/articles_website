from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm

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
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template(template_name, title=title, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    template_name = "login.html"
    title="Авторизация"
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


@app.route("/")
def index():
    return render_template("index.html", title="main")


if __name__ == '__main__':
    db_session.global_init("db/articles.db")
    app.run()
