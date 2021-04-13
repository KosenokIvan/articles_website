from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "comments"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id",
                                                                         ondelete="CASCADE"))
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("articles.id",
                                                                             ondelete="CASCADE"))
    text = sqlalchemy.Column(sqlalchemy.String(512))
    image = sqlalchemy.Column(sqlalchemy.String(256))
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    user = orm.relation("User")
    article = orm.relation("Article")
