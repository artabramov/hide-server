"""Module defines class contains error messages."""


class E:
    """Class contains error messages."""

    INTERNAL_SERVER_ERROR = "Internal server error"

    LOGIN_INVALID = "Login or password is invalid"
    LOGIN_DENIED = "Login denied due to user role permissions"
    LOGIN_SUSPENDED = "Login attempts are temporarily suspended"

    VALUE_EMPTY = "The value is empty"
    VALUE_EXISTS = "The value already exists"
    VALUE_INVALID = "The value is invalid"
