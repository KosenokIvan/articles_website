from io import BytesIO
from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from parsers import add_article_parser, get_article_parser, put_article_parser
from model_workers.article import ArticleModelWorker
from tools.errors import ArticleNotFoundError, ForbiddenToUserError
from tools.image_to_byte_array import image_to_byte_array
from tools.hex_image_to_file_storage import hex_image_to_file_storage
from tools.constants import ARTICLES_IMAGES_DIR


class ArticleResource(Resource):
    def get(self, article_id):
        args = get_article_parser.parser.parse_args()
        try:
            article = ArticleModelWorker.get_article(article_id, args["get_field"])
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article {article_id} not found")
        else:
            if "image" in article:
                if article["image"] is not None:
                    article["image"] = image_to_byte_array(
                        f"{ARTICLES_IMAGES_DIR}/{article['image']}"
                    ).hex()
            return jsonify({"article": article})

    @login_required
    def put(self, article_id):
        args = put_article_parser.parser.parse_args()
        article_data = {}
        keys = ("title", "content")
        for key in keys:
            if key in args:
                article_data[key] = args[key]
        if args.get("image") is not None:
            article_data["image"] = hex_image_to_file_storage(args["image"])
        try:
            ArticleModelWorker.edit_article(article_id, current_user.id, article_data)
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article {article_id} not found")
        except ForbiddenToUserError:
            fr_abort(403, message=f"User {current_user.id} is not author of article {article_id}")
        else:
            return jsonify({"success": "ok"})

    @login_required
    def delete(self, article_id):
        try:
            ArticleModelWorker.delete_article(article_id, current_user.id)
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article {article_id} not found")
        except ForbiddenToUserError:
            fr_abort(403, message=f"User {current_user.id} is not author of article {article_id}")
        else:
            return jsonify({"success": "ok"})


class ArticlesListResource(Resource):
    @login_required
    def post(self):
        args = add_article_parser.parser.parse_args()
        article_data = {
            "title": args["title"],
            "content": args["content"],
            "author": current_user.id
        }
        if args.get("image") is not None:
            article_data["image"] = hex_image_to_file_storage(args["image"])
        ArticleModelWorker.new_article(article_data)
        return jsonify({"success": "ok"})

    def get(self):
        args = get_article_parser.parser.parse_args()
        articles = ArticleModelWorker.get_all_articles(args["get_field"])
        if "image" in args["get_field"]:
            for article in articles:
                if article["image"] is not None:
                    article["image"] = image_to_byte_array(
                        f"{ARTICLES_IMAGES_DIR}/{article['image']}"
                    ).hex()
        return jsonify({"articles": articles})
