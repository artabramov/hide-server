"""Module defines class contains error messages."""


class E:
    """Class contains error messages."""

    INTERNAL_SERVER_ERROR = "Internal server error"

    USER_LOGIN_INVALID = "User login is invalid"
    USER_LOGIN_DENIED = "Login denied due to user role permissions"
    USER_LOGIN_SUSPENDED = "Login attempts are temporarily suspended"
    USER_PASS_INVALID = "User password is invalid"
    USER_TOTP_INVALID = "Time-based one-time password is invalid"

    JWT_EMPTY = "The token is missing or empty"
    JWT_INVALID = "The token has invalid format"
    JWT_EXPIRED = "The token has expired"
    JWT_REJECTED = "The token contains invalid user data"
    JWT_DENIED = "The token does not have enough permissions"

    VALUE_EMPTY = "The value is empty"
    VALUE_EXISTS = "The value already exists"
    VALUE_INVALID = "The value is invalid"
