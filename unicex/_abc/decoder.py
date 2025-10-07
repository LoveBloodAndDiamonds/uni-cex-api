__all__ = ["IDecoder"]

from typing import Protocol


class IDecoder(Protocol):
    """Протокол для декодеров сообщений c вебсокета."""

    def decode(self, message: bytes | str) -> dict:
        """Декодирует сообщение.

        Параметры:
            message (`Any`): Сообщение для декодирования.

        Возвращает:
            `Any`: Декодированное сообщение.
        """
        ...
