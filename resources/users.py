from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import login_required, current_user
from model_workers.user import UserModelWorker
from parsers import login_parser, register_parser, get_user_parser, put_user_parser
from tools.errors import UserNotFoundError, IncorrectPasswordError, PasswordMismatchError, \
    UserAlreadyExistError, EmailAlreadyUseError
from tools.hex_image_to_file_storage import hex_image_to_file_storage
from tools.image_to_byte_array import image_to_byte_array
from tools.constants import USERS_AVATARS_DIR


class LoginResource(Resource):
    def post(self):
        args = login_parser.parser.parse_args()
        try:
            UserModelWorker.login({
                "email": args["email"],
                "password": args["password"],
                "remember_me": args["remember_me"]
            })
        except UserNotFoundError:
            fr_abort(404, message="Incorrect email or password")
        except IncorrectPasswordError:
            fr_abort(404, message="Incorrect email or password")
        else:
            return jsonify({"success": "ok"})


class UserResource(Resource):
    def get(self, user_id):
        args = get_user_parser.parser.parse_args()
        if current_user.is_authenticated and current_user.id == user_id:
            fields = ("id", "name", "surname", "nickname", "email", "description", "avatar")
        else:
            fields = ("id", "nickname", "description", "avatar")
        fields = (field for field in fields if field in args["get_field"])
        try:
            user = UserModelWorker.get_user(user_id, fields)
        except UserNotFoundError:
            fr_abort(404, message=f"User {user_id} not found")
        else:
            return jsonify({"user": user})

    @login_required
    def put(self, user_id):
        args = put_user_parser.parser.parse_args()
        if current_user.id != user_id:
            fr_abort(403, message=f"User {current_user.id} can't edit page of the user {user_id}")
        user_data = {
                "name": args["name"],
                "surname": args["surname"],
                "nickname": args["nickname"],
                "email": args["email"],
                "new_password": args["new_password"],
                "new_password_again": args["new_password_again"],
                "description": args["description"],
                "password": args["password"]
            }
        if args.get("avatar") is not None:
            user_data["avatar"] = hex_image_to_file_storage(args["avatar"])
        try:
            UserModelWorker.edit_user(user_id, user_data)
        except IncorrectPasswordError:
            fr_abort(400, message="Incorrect password")
        except PasswordMismatchError:
            fr_abort(400, message="Password mismatch")
        except UserAlreadyExistError:
            fr_abort(400, message=f"User @{args['nickname']} already exist")
        except EmailAlreadyUseError:
            fr_abort(400, message=f"Email {args['email']} already use")
        else:
            return jsonify({"success": "ok"})

    @login_required
    def delete(self, user_id):
        if current_user.id != user_id:
            fr_abort(403, message=f"User {current_user.id} can't edit page of the user {user_id}")
        try:
            UserModelWorker.delete_user(user_id)
        except UserNotFoundError:
            fr_abort(404, message=f"User {user_id} not found")
        return jsonify({"success": "ok"})


class UsersListResource(Resource):
    def post(self):
        args = register_parser.parser.parse_args()
        user_data = {
            "name": args["name"],
            "surname": args["surname"],
            "nickname": args["nickname"],
            "email": args["email"],
            "password": args["password"],
            "password_again": args["password_again"],
            "description": args["description"]
        }
        if args.get("avatar") is not None:
            user_data["avatar"] = hex_image_to_file_storage(args["avatar"])
        try:
            UserModelWorker.new_user(user_data)
        except PasswordMismatchError:
            fr_abort(400, message="Password mismatch")
        except UserAlreadyExistError:
            fr_abort(400, message=f"User @{args['nickname']} already exist")
        except EmailAlreadyUseError:
            fr_abort(400, message=f"Email {args['email']} already use")
        else:
            return jsonify({"success": "ok"})

    def get(self):
        args = get_user_parser.parser.parse_args()
        fields = tuple(field for field in ("id", "nickname", "description", "avatar")
                       if field in args["get_field"])
        users = UserModelWorker.get_all_users(fields)
        if "avatar" in fields:
            for user in users:
                if user["avatar"] is not None:
                    user["avatar"] = image_to_byte_array(
                        f"{USERS_AVATARS_DIR}/{user['avatar']}"
                    ).hex()
        return jsonify({"users": users})
