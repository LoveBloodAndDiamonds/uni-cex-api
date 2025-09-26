"""Модуль,который описывает исключения и ошибки, которые могут возникнуть при работе с библиотекой."""

from dataclasses import dataclass, field


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


@dataclass
class ResponseError(UniCexException):
    """Исключение, возникающее при ошибке ответа."""

    status_code: int
    code: str = ""  # "" - means undefined
    response_json: dict = field(default_factory=dict)
    response_text: str = ""

    def __str__(self) -> str:
        """Возвращает строковое представление исключения."""
        if self.response_json:
            preview = str(self.response_json)
            if len(preview) > 500:
                preview = preview[:500] + "..."
            return f"ResponseError: status_code={self.status_code}, code={self.code}, response_json: {preview}"
        elif self.response_text:
            preview = str(self.response_text)
            if len(preview) > 500:
                preview = preview[:500] + "..."
            return f"ResponseError: status_code={self.status_code}, code={self.code}, response_text: {preview}"
        else:
            return f"ResponseError: status_code={self.status_code}, code={self.code}"
