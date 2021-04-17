class PasswordMismatchError(Exception):
    pass


class EmailAlreadyUseError(Exception):
    pass


class UserAlreadyExistError(Exception):
    pass


class IncorrectPasswordError(Exception):
    pass


class ArticleNotFoundError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass


class LikeAlreadyThereError(Exception):
    pass


class LikeNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class ForbiddenToUserError(Exception):
    pass
