from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

parser = reqparse.RequestParser()
parser.add_argument("title", type=str, required=True)
parser.add_argument("content", type=str,  required=True)
parser.add_argument("image", type=str)
