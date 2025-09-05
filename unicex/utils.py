import hashlib
import hmac


def hmac_hashing(api_secret: str, payload: str) -> str:
    """Generates an HMAC-SHA256 hash of the provided payload using the given API secret.

    Args:
        api_secret (str): The API secret to use for the HMAC-SHA256 hashing.
        payload (str): The payload to hash.

    Returns:
        str: The hexadecimal HMAC-SHA256 hash of the payload.

    """
    m = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256)
    return m.hexdigest()
