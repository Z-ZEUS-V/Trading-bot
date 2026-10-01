"""Validate a Kraken Pro (spot REST) API key with a read-only endpoint.

Prompts hide credentials; no key, secret, account identifier, or response body is
printed or written to disk. The request only calls GetApiKeyInfo and cannot trade.
"""

from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


URL = "https://api.kraken.com/0/private/GetApiKeyInfo"
URI_PATH = "/0/private/GetApiKeyInfo"
TIMEOUT_SECONDS = 15
STANDARD_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def _api_sign(secret_b64: str, nonce: str, post_data: str) -> str:
    compact_secret = "".join(secret_b64.split())
    padded_secret = compact_secret + ("=" * (-len(compact_secret) % 4))
    secret = base64.b64decode(padded_secret, altchars=b"-_", validate=True)
    digest = hashlib.sha256((nonce + post_data).encode("utf-8")).digest()
    signature = hmac.new(secret, URI_PATH.encode("utf-8") + digest, hashlib.sha512).digest()
    return base64.b64encode(signature).decode("ascii")


def main() -> int:
    print("Kraken Pro (Spot REST): comprobación de clave (solo lectura).")
    print("Las credenciales se piden sin mostrarse y no se guardan.\n")
    api_key = getpass.getpass("API key de Kraken Pro: ").strip()
    api_secret = getpass.getpass("API secret privada: ").strip()
    if not api_key or not api_secret:
        print("Resultado: faltan credenciales.")
        return 2

    nonce = str(time.time_ns() // 1_000_000)
    params = {"nonce": nonce}
    otp = getpass.getpass("OTP de la API (Enter si no configuraste uno): ").strip()
    if otp:
        params["otp"] = otp
    post_data = urlencode(params)

    try:
        signature = _api_sign(api_secret, nonce, post_data)
    except (ValueError, base64.binascii.Error):
        print(
            "Resultado: no se pudo decodificar el secret como Base64. "
            "Comprueba que en el segundo prompt introdujiste el Private/API Secret completo, "
            "no la Public/API Key. No se envió ninguna petición a Kraken."
        )
        return 2

    request = Request(
        URL,
        data=post_data.encode("ascii"),
        headers={
            "API-Key": api_key,
            "API-Sign": signature,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": STANDARD_USER_AGENT,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 401:
            print("Resultado: Kraken Pro no autenticó la clave. Puede ser una clave Futures, un par incorrecto o firma/OTP inválidos.")
        elif exc.code == 403:
            print("Resultado: HTTP 403 (acceso bloqueado); puede ser una protección de Kraken/Cloudflare. No confirma por sí solo que la clave sea inválida.")
        else:
            print(f"Resultado: Kraken respondió HTTP {exc.code}; no se pudo confirmar la clave.")
        return 1
    except (URLError, TimeoutError, OSError):
        print("Resultado: no se pudo alcanzar Kraken; comprueba la conexión e inténtalo de nuevo.")
        return 1
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Resultado: Kraken respondió con un formato inesperado.")
        return 1

    errors = payload.get("error") or []
    info = payload.get("result") or {}
    if errors or not info:
        print("Resultado: Kraken Pro rechazó la autenticación o la respuesta no confirmó la clave.")
        if errors:
            print("Código de error:", ", ".join(str(error) for error in errors))
        return 1

    permissions = sorted(info.get("permissions") or [])
    print("Resultado: clave autenticada por Kraken Pro (Spot REST API).")
    print("Permisos declarados:", ", ".join(permissions) if permissions else "ninguno")
    print("No se muestran ni guardan el identificador de cuenta, la clave ni el secret.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nComprobación cancelada; no se realizó ninguna operación de trading.")
        raise SystemExit(130)
