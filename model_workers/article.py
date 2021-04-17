from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from data.articles import Article
from data import db_session
from tools.errors import ArticleNotFoundError, ForbiddenToUserError
from tools.get_image_path import get_image_path
from tools.constants import ARTICLES_IMAGES_DIR


class ArticleModelWorker:
    @staticmethod
    def get_article(article_id, fields=("id", "title")):
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        return article.to_dict(only=fields)

    @staticmethod
    def get_all_articles(fields=("id", "title")):
        db_sess = db_session.create_session()
        articles = db_sess.query(Article).all()
        return [article.to_dict(only=fields) for article in articles]

    @staticmethod
    def new_article(article_data):
        db_sess = db_session.create_session()
        article = Article(
            title=article_data["title"],
            content=article_data["content"],
            author=article_data["author"]
        )
        if article_data.get("image") is not None:
            image = Image.open(BytesIO(article_data["image"].read()))
            filename = get_image_path(ARTICLES_IMAGES_DIR)
            image.save(f"{ARTICLES_IMAGES_DIR}/{filename}")
            article.image = filename
        db_sess.add(article)
        db_sess.commit()

    @staticmethod
    def edit_article(article_id, user_id, article_data):
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        if article.author != user_id:
            raise ForbiddenToUserError
        if "title" in article_data and article_data["title"]:
            article.title = article_data["title"]
        if "content" in article_data and article_data["content"]:
            article.content = article_data["content"]
        if "image" in article_data and article_data["image"]:
            image = Image.open(BytesIO(article_data["image"].read()))
            filename = get_image_path(ARTICLES_IMAGES_DIR)
            image.save(f"{ARTICLES_IMAGES_DIR}/{filename}")
            if article.image:
                os.remove(f"{ARTICLES_IMAGES_DIR}/{article.image}")
            article.image = filename
        db_sess.commit()

    @staticmethod
    def delete_article(article_id, user_id):
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        if article.author != user_id:
            raise ForbiddenToUserError
        if article.image:
            os.remove(f"{ARTICLES_IMAGES_DIR}/{article.image}")
        db_sess.delete(article)
        db_sess.commit()

    @staticmethod
    def update_likes_count(article_id, likes_delta):
        db_sess = db_session.create_session()
        article = db_sess.query(Article).get(article_id)
        if not article:
            raise ArticleNotFoundError
        article.likes_count += likes_delta
        db_sess.commit()
