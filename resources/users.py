from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from model_workers.user import UserModelWorker
from parsers import login_parser
from tools.errors import UserNotFoundError, IncorrectPasswordError


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
