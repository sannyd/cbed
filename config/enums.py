from enum import IntEnum


class BaseEnum(IntEnum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]


class LoginType(BaseEnum):
    EMAIL_PASSWORD = 1
    GOOGLE = 2
    FACEBOOK = 3
    PHONE = 4
    APPLE = 5


class PhoneAuthType(BaseEnum):
    REGISTER = 1
    LOGIN = 2
