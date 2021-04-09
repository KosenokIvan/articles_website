from datetime import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "articles"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    image = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relation("User")
