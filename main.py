from flask import Flask, render_template
from data import db_session

app = Flask(__name__)
app.config["SECRET_KEY"] = "articles_site"


@app.route("/")
def index():
    return render_template("index.html", title="main")


if __name__ == '__main__':
    db_session.global_init("db/articles.db")
    app.run()
