"""Модуль,который описывает исключения и ошибки, которые могут возникнуть при работе с библиотекой."""

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


@dataclass
class AdapterError(UniCexException):
    """Исключение, возникающее при ошибке адаптации данных."""

    pass


@dataclass
class QueueOverflowError(UniCexException):
    """Исключение, возникающее при переполнении очереди сообщений."""

    pass
