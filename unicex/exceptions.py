from dataclasses import dataclass


@dataclass
class UniCexException(Exception):
    """Базовое исключение библиотеки."""

    message: str
    """Сообщение об ошибке."""


@dataclass
class NotAuthorized(UniCexException):
    """Исключение, возникающее при отсутствии авторизации."""

    pass


@dataclass
class NotSupported(UniCexException):
    """Исключение, возникающее при попытке использования не поддерживаемой функции."""

    pass
