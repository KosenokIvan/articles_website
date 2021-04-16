from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from parsers import add_article_parser, get_article_parser
from model_workers.article import ArticleModelWorker
from tools.errors import ArticleNotFoundError
from tools.image_to_byte_array import image_to_byte_array
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
