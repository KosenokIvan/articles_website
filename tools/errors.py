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
