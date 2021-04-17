from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("get_field", action="append",
                    choices=["id", "name", "surname", "nickname", "email", "description", "avatar"],
                    default=["id", "nickname"])
