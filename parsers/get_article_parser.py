from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("get_field", action="append",
                    choices=["id", "title", "content", "image"], default=["id", "title"])
