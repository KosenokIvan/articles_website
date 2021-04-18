from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from parsers import get_comment_parser
from tools.image_to_byte_array import image_to_byte_array
from tools.constants import COMMENTS_IMAGES_DIR
from model_workers.comment import CommentModelWorker


class CommentResource(Resource):
    pass


class CommentsListResource(Resource):
    def get(self):
        args = get_comment_parser.find_parser.parse_args()
        comments = CommentModelWorker.get_all_comments(args["get_field"], args["author"],
                                                       args["article"], args["limit"],
                                                       args["offset"])
        if "image" in args["get_field"]:
            for comment in comments:
                if comment["image"] is not None:
                    comment["image"] = image_to_byte_array(
                        f"{COMMENTS_IMAGES_DIR}/{comment['image']}"
                    ).hex()
        return jsonify({"comments": comments})
