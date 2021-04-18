from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument("get_field", action="append",
                    choices=["id", "name", "surname", "nickname", "email",
                             "description", "avatar", "modified_date"],
                    default=["id", "nickname"])

range_parser = parser.copy()
range_parser.add_argument("limit", type=int)
range_parser.add_argument("offset", type=int)

find_parser = range_parser.copy()
find_parser.add_argument("nickname_search_string", type=str)
find_parser.add_argument("nickname_filter",
                         choices=["equals", "starts", "ends", "contains", "equals_case_insensitive"],
                         default="equals")
