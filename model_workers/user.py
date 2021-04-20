from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from datetime import datetime
from PIL import Image
from flask_login import login_user
from data.users import User
from data import db_session
from tools.errors import PasswordMismatchError, EmailAlreadyUseError, \
    UserAlreadyExistError, IncorrectPasswordError, UserNotFoundError, \
    UnknownFilterError, IncorrectNicknameLengthError, NicknameContainsInvalidCharactersError, \
    IncorrectPasswordLengthError, NotSecurePasswordError
from tools.get_image_path import get_image_path
from tools.constants import USERS_AVATARS_DIR
from model_workers.article_like import ArticleLikeModelWorker


def check_nickname(nickname):
    if not(3 <= len(nickname) <= 32):
        raise IncorrectNicknameLengthError
    valid_characters = ascii_letters + digits + "_"
    if any(map(lambda x: x not in valid_characters, nickname)):
        raise NicknameContainsInvalidCharactersError


def check_password(password):
    if not(8 <= len(password) <= 512):
        raise IncorrectPasswordLengthError
    if not password.strip():
        raise NotSecurePasswordError


class UserModelWorker:
    @staticmethod
    def get_user(user_id, fields=("id", "nickname")):
        if not fields:
            fields = ("id",)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            raise UserNotFoundError
        return user.to_dict(only=fields)

    @staticmethod
    def get_all_users(fields=("id", "nickname"), limit=None, offset=None,
                      nickname_search_string=None, nickname_filter="equals"):
        if not fields:
            fields = ("id",)
        db_sess = db_session.create_session()
        users = db_sess.query(User)
        if nickname_search_string is not None:
            if nickname_filter == "equals":
                users = users.filter(User.nickname == nickname_search_string)
            elif nickname_filter == "equals_case_insensitive":
                users = users.filter(User.nickname.like(nickname_search_string))
            elif nickname_filter == "starts":
                users = users.filter(User.nickname.like(f"{nickname_search_string}%"))
            elif nickname_filter == "ends":
                users = users.filter(User.nickname.like(f"%{nickname_search_string}"))
            elif nickname_filter == "contains":
                users = users.filter(User.nickname.like(f"%{nickname_search_string}%"))
            else:
                raise UnknownFilterError(f"Unknown filter: {nickname_filter}")
        if offset is not None:
            users = users.offset(offset)
        if limit is not None:
            users = users.limit(limit)
        return [user.to_dict(only=fields) for user in users]

    @staticmethod
    def login(user_data):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            raise UserNotFoundError
        if not user.check_password(user_data["password"]):
            raise IncorrectPasswordError
        login_user(user, remember=user_data["remember_me"])

    @staticmethod
    def new_user(user_data):
        if user_data["password"] != user_data["password_again"]:
            raise PasswordMismatchError
        check_password(user_data["password"])
        check_nickname(user_data["nickname"])
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == user_data["email"]).first():
            raise EmailAlreadyUseError
        if db_sess.query(User).filter(User.nickname == user_data["nickname"]).first():
            raise UserAlreadyExistError
        user = User(name=user_data["name"],
                    surname=user_data["surname"],
                    nickname=user_data["nickname"],
                    email=user_data["email"])
        user.set_password(user_data["password"])
        if user_data.get("avatar"):
            image = Image.open(BytesIO(user_data["avatar"].read()))
            filename = get_image_path(USERS_AVATARS_DIR)
            image.save(f"{USERS_AVATARS_DIR}/{filename}")
            user.avatar = filename
        if user_data.get("description") is not None:
            user.description = user_data["description"]
        db_sess.add(user)
        db_sess.commit()

    @staticmethod
    def edit_user(user_id, user_data):
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user.check_password(user_data["password"]):
            raise IncorrectPasswordError
        if db_sess.query(User).filter(
                User.email == user_data["email"], User.id != user_id
        ).first():
            raise EmailAlreadyUseError
        if db_sess.query(User).filter(
                User.nickname == user_data["nickname"], User.id != user_id
        ).first():
            raise UserAlreadyExistError
        if user_data.get("nickname") is not None:
            check_nickname(user_data["nickname"])
        if user_data.get("new_password"):
            check_password(user_data["new_password"])
            if user_data["new_password"] != user_data.get("new_password_again"):
                raise PasswordMismatchError
            user.set_password(user_data["new_password"])
        if user_data.get("name") is not None:
            user.name = user_data.get("name", user.name)
        if user_data.get("surname") is not None:
            user.surname = user_data.get("surname", user.surname)
        if user_data.get("nickname") is not None:
            user.nickname = user_data.get("nickname", user.nickname)
        if user_data.get("email") is not None:
            user.email = user_data.get("email", user.email)
        if user_data.get("description") is not None:
            user.description = user_data.get("description", user.description)
        user.modified_date = datetime.now()
        if user_data.get("avatar"):
            image = Image.open(BytesIO(user_data["avatar"].read()))
            filename = get_image_path(USERS_AVATARS_DIR)
            if user.avatar:
                os.remove(f"{USERS_AVATARS_DIR}/{user.avatar}")
            user.avatar = filename
            image.save(f"{USERS_AVATARS_DIR}/{user.avatar}")
        db_sess.commit()

    @staticmethod
    def delete_user(user_id, user_password):
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            raise UserNotFoundError
        if not user.check_password(user_password):
            raise IncorrectPasswordError
        if user.avatar is not None:
            os.remove(f"{USERS_AVATARS_DIR}/{user.avatar}")
        for like in user.likes:
            ArticleLikeModelWorker.delete_like({
                "user_id": user_id,
                "article_id": like.article_id
            })
        db_sess.delete(user)
        db_sess.commit()
