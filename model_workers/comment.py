from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from data.comments import Comment
from data import db_session
from tools.errors import CommentNotFoundError
from tools.get_image_path import get_image_path
from tools.constants import COMMENTS_IMAGES_DIR


class CommentModelWorker:
    @staticmethod
    def new_comment(comment_data):
        db_sess = db_session.create_session()
        comment = Comment(
            author=comment_data["author"],
            article_id=comment_data["article_id"],
            text=comment_data["text"]
        )
        if comment_data["image"]:
            image = Image.open(BytesIO(comment_data["image"].read()))
            filename = get_image_path(COMMENTS_IMAGES_DIR)
            image.save(f"{COMMENTS_IMAGES_DIR}/{filename}")
            comment.image = filename
        db_sess.add(comment)
        db_sess.commit()

    @staticmethod
    def edit_comment(comment_id, comment_data):
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        if not comment:
            raise CommentNotFoundError
        comment.text = comment_data["text"]
        if comment_data["image"]:
            image = Image.open(BytesIO(comment_data["image"].read()))
            filename = get_image_path(COMMENTS_IMAGES_DIR)
            image.save(f"{COMMENTS_IMAGES_DIR}/{filename}")
            if comment.image:
                os.remove(f"{COMMENTS_IMAGES_DIR}/{comment.image}")
            comment.image = filename
        db_sess.commit()

    @staticmethod
    def delete_comment(comment_id):
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).get(comment_id)
        if not comment:
            raise CommentNotFoundError
        if comment.image:
            os.remove(f"{COMMENTS_IMAGES_DIR}/{comment.image}")
        db_sess.delete(comment)
        db_sess.commit()
