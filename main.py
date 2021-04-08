from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "articles_site"


if __name__ == '__main__':
    app.run()
