class UserNotFound(Exception):
    detail = 'User not found'


class UserAlreadyExistsException(Exception):
    detail = 'User with this username already exists'


class UserIncorrectPasswordException(Exception):
    detail = 'Incorrect password'


class TokenExpiredException(Exception):
    detail = 'Token has expired'


class InvalidTokenException(Exception):
    detail = 'Token is invalid'


class LinkNotFound(Exception):
    detail = 'Link not found'


class UserIsNotLinkOwner(Exception):
    detail = 'User is not owner of this link'


class CustomLinkAlreadyExists(Exception):
    detail = 'Link with this alias already exists'


class ShortLinkGenerationException(Exception):
    pass
