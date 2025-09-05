__all__ = [
    "dict_to_query_string",
    "generate_hmac_sha256_signature",
    "filter_params",
]

import hashlib
import hmac
import json
from urllib.parse import urlencode


def filter_params(params: dict) -> dict:
    """Фильтрует параметры запроса, удаляя None-значения.

    Параметры:
        params (dict): Словарь параметров запроса.

    Возвращает:
        dict: Отфильтрованный словарь параметров запроса.
    """
    return {k: v for k, v in params.items() if v is not None}


def dict_to_query_string(params: dict) -> str:
    """Преобразует словарь параметров в query string для URL.

    - Списки и словари автоматически сериализуются в JSON.
    - Используется стандартная urlencode кодировка.

    Параметры:
        params (dict): Словарь параметров запроса.

    Возвращает:
        str: Строка параметров, готовая для использования в URL.
    """
    processed = {
        k: json.dumps(v, separators=(",", ":")) if isinstance(v, list | dict) else v
        for k, v in params.items()
    }
    return urlencode(processed, doseq=True)


def generate_hmac_sha256_signature(secret_key: str, payload: str) -> str:
    """Генерирует HMAC-SHA256 подпись для переданного payload с использованием секретного ключа.

    Параметры:
        secret_key (str): Секретный ключ API.
        payload (str): Строка запроса или тело, которое нужно подписать.

    Возвращает:
        str: Подпись в виде шестнадцатеричной строки.
    """
    return hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
