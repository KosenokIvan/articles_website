from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from data.articles import Article
from data import db_session
from tools.errors import ArticleNotFoundError
from tools.get_image_path import get_image_path
from tools.constants import ARTICLES_IMAGES_DIR


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
            filename = get_image_path(ARTICLES_IMAGES_DIR)
            image.save(f"{ARTICLES_IMAGES_DIR}/{filename}")
            article.image = filename
        db_sess.add(article)
        db_sess.commit()

    @staticmethod
    def edit_article(article_id, article_data):
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        article.title = article_data["title"]
        article.content = article_data["content"]
        if article_data["image"]:
            image = Image.open(BytesIO(article_data["image"].read()))
            filename = get_image_path(ARTICLES_IMAGES_DIR)
            image.save(f"{ARTICLES_IMAGES_DIR}/{filename}")
            if article.image:
                os.remove(f"{ARTICLES_IMAGES_DIR}/{article.image}")
            article.image = filename
        db_sess.commit()

    @staticmethod
    def delete_article(article_id):
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        if article.image:
            os.remove(f"{ARTICLES_IMAGES_DIR}/{article.image}")
        db_sess.delete(article)
        db_sess.commit()