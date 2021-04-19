from flask import jsonify
from flask_restful import abort as fr_abort, Resource
from flask_login import current_user, login_required
from model_workers.article_like import ArticleLikeModelWorker
from tools.errors import ArticleNotFoundError, LikeNotFoundError, LikeAlreadyThereError


class ArticleLikeResource(Resource):
    @login_required
    def get(self, article_id):
        return jsonify({"like_exist": ArticleLikeModelWorker.like_exist({
            "article_id": article_id,
            "user_id": current_user.id
        })})

    @login_required
    def post(self, article_id):
        try:
            ArticleLikeModelWorker.new_like({
                "article_id": article_id,
                "user_id": current_user.id
            })
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article {article_id} not found")
        except LikeAlreadyThereError:
            fr_abort(400, message="Like already there")
        else:
            return jsonify({"success": "ok"})

    @login_required
    def delete(self, article_id):
        try:
            ArticleLikeModelWorker.delete_like({
                "article_id": article_id,
                "user_id": current_user.id
            })
        except ArticleNotFoundError:
            fr_abort(404, message=f"Article {article_id} not found")
        except LikeNotFoundError:
            fr_abort(400, message="Like not found")
        else:
            return jsonify({"success": "ok"})
