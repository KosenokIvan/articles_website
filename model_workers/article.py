from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from data.articles import Article
from data import db_session


class ArticleModelWorker:
    @staticmethod
    def new_article(article_data):
        db_sess = db_session.create_session()
        article = Article(
            title=article_data["title"],
            content=article_data["content"],
            author=article_data["author"]
        )
        if article_data["image"]:
            image = Image.open(BytesIO(article_data["image"].read()))
            while True:
                filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
                if not os.path.exists(f"static/img/articles_images/{filename}"):
                    break
            image.save(f"static/img/articles_images/{filename}")
            article.image = filename
        db_sess.add(article)
        db_sess.commit()
