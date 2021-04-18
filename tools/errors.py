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


class UnknownFilterError(Exception):
    pass


class ForbiddenToUserError(Exception):
    pass


class IncorrectNicknameLengthError(Exception):
    pass


class NicknameContainsInvalidCharactersError(Exception):
    pass


class IncorrectPasswordLengthError(Exception):
    pass


class NotSecurePasswordError(Exception):
    pass
