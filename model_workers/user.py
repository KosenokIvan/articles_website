from random import choices
from string import ascii_letters, digits
import os
from io import BytesIO
from PIL import Image
from data.users import User
from data import db_session
from tools.errors import PasswordMismatchError, EmailAlreadyUseError, \
    UserAlreadyExistError, IncorrectPasswordError


class UserModelWorker:
    @staticmethod
    def new_user(user_data):
        if user_data["password"] != user_data["password_again"]:
            raise PasswordMismatchError
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
        if user_data["avatar"]:
            image = Image.open(BytesIO(user_data["avatar"].read()))
            while True:
                filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
                if not os.path.exists(f"static/img/avatars/{filename}"):
                    break
            image.save(f"static/img/avatars/{filename}")
            user.avatar = filename
        if user_data["description"]:
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
        if user_data["new_password"]:
            if user_data["new_password"] != user_data["new_password_again"]:
                raise PasswordMismatchError
            user.set_password(user_data["new_password"])
        user.name = user_data["name"]
        user.surname = user_data["surname"]
        user.nickname = user_data["nickname"]
        user.email = user_data["email"]
        user.description = user_data["description"]
        if user_data["avatar"]:
            image = Image.open(BytesIO(user_data["avatar"].read()))
            while True:
                filename = f"{''.join(choices(ascii_letters + digits, k=64))}.png"
                if not os.path.exists(f"static/img/avatars/{filename}"):
                    break
            os.remove(f"static/img/avatars/{user.avatar}")
            user.avatar = filename
            image.save(f"static/img/avatars/{user.avatar}")
        db_sess.commit()
