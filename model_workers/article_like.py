from data.likes import ArticleLike
from data.articles import Article
from data import db_session
from tools.errors import LikeAlreadyThereError, LikeNotFoundError, ArticleNotFoundError


class ArticleLikeModelWorker:
    @staticmethod
    def new_like(like_data):
        db_sess = db_session.create_session()
        if db_sess.query(ArticleLike).filter(
                ArticleLike.user_id == like_data["user_id"],
                ArticleLike.article_id == like_data["article_id"]
        ).first():
            raise LikeAlreadyThereError
        if not db_sess.query(Article).get(like_data["article_id"]):
            raise ArticleNotFoundError
        like = ArticleLike(
            user_id=like_data["user_id"],
            article_id=like_data["article_id"]
        )
        db_sess.add(like)
        db_sess.commit()

    @staticmethod
    def delete_like(like_data):
        db_sess = db_session.create_session()
        like = db_sess.query(ArticleLike).filter(
            ArticleLike.user_id == like_data["user_id"],
            ArticleLike.article_id == like_data["article_id"]
        ).first()
        if not like:
            raise LikeNotFoundError
        db_sess.delete(like)
        db_sess.commit()
