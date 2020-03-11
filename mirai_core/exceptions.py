class MiraiException(Exception):
    """
    Generic exception
    """
    pass


class NetworkException(MiraiException):
    """
    Exceptions such as not able to reach mirai, possibly due to service not started or incorrect ip/port
    """
    pass


class AuthenticationException(MiraiException):
    """
    Exceptions such as incorrect auth_key
    """
    pass


class SessionException(MiraiException):
    """
    Exceptions such as incorrect session_key
    """
    pass


class PrivilegeException(MiraiException):
    """
    You do not have permission to perform such action (such as mute, kick, etc.)
    """
    pass


class UnknownTargetException(MiraiException):
    """
    Target not found (sending to non-existing group, friend, etc.)
    """
    pass


class BadRequestException(MiraiException):
    """
    Request contains invalid parameter
    """
    pass


class ServerException(MiraiException):
    """
    Server is returning non 200 return code, see console log for more details
    This is more likely to be mirai side issue, but sometimes incorrect parameters can cause this problem too
    """
    pass
