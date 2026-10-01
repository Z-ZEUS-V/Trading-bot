"""Check Kraken Derivatives API credentials with its read-only key-check endpoint.

The API key and secret are prompted without echo, used only in memory, and never
printed or written to disk. This script performs one GET request and cannot trade.
"""

from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://futures.kraken.com"
API_BASE_PATH = "/api/auth/v1"
# Kraken's authent signs the endpoint path relative to its API base URL.
ENDPOINT_PATH = "/api-keys/v3/check"
TIMEOUT_SECONDS = 15
STANDARD_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def _authent(secret_b64: str, endpoint_path: str) -> str:
    """Build Kraken Futures Authent for the no-body, no-nonce key-check GET."""
    # Pasting from a wrapped UI can include whitespace; remove it without ever
    # printing the value. Accept standard and URL-safe Base64 plus omitted padding.
    # Some Windows PowerShell console hosts pass Ctrl+V (U+0016) through as
    # input instead of pasting the clipboard while getpass hides the prompt.
    # U+0016 cannot be part of a Base64 secret, so discard that paste control.
    compact_secret = "".join(secret_b64.split()).replace("\x16", "")
    padded_secret = compact_secret + ("=" * (-len(compact_secret) % 4))
    secret = base64.b64decode(padded_secret, altchars=b"-_", validate=True)
    message = endpoint_path.encode("utf-8")  # postData and nonce are empty.
    digest = hashlib.sha256(message).digest()
    signature = hmac.new(secret, digest, hashlib.sha512).digest()
    return base64.b64encode(signature).decode("ascii")


def main() -> int:
    print("Kraken Derivatives API: comprobación de autenticación (solo lectura).")
    print("Las credenciales se introducen sin mostrarse y no se guardan.\n")
    # A companion PowerShell launcher can collect paste-safe SecureString
    # inputs, then pass them through process-scoped environment variables.
    # Consume and remove those variables immediately.
    api_key = os.environ.pop("KRAKEN_FUTURES_API_KEY", "")
    api_secret = os.environ.pop("KRAKEN_FUTURES_API_SECRET", "")
    if not api_key and not api_secret:
        api_key = getpass.getpass("API key pública de Derivatives: ").strip().replace("\x16", "")
        api_secret = getpass.getpass("API secret privada de Derivatives: ").strip().replace("\x16", "")
    api_key = "".join(api_key.split()).replace("\x16", "")
    missing = []
    if not api_key:
        missing.append("API key pública")
    if not api_secret:
        missing.append("API secret privada")
    if missing:
        print("Resultado: no se recibió el campo: " + " y ".join(missing) + ". No se envió ninguna petición a Kraken.")
        return 2

    key_alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-")
    invalid_key = [f"U+{ord(ch):04X}" for ch in api_key if ch not in key_alphabet]
    if invalid_key:
        print(
            "Resultado: la API key contiene carácter(es) fuera del formato Base64 "
            f"({', '.join(invalid_key)}). No se envió ninguna petición."
        )
        return 2

    try:
        # Decode once locally first, then sign each documented path form below.
        _authent(api_secret, ENDPOINT_PATH)
    except (ValueError, base64.binascii.Error):
        compact_secret = "".join(api_secret.split())
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-")
        invalid_codepoints = [
            f"U+{ord(character):04X}"
            for character in compact_secret
            if character not in allowed
        ]
        if invalid_codepoints:
            reason = (
                "el texto contiene carácter(es) fuera del alfabeto Base64 "
                f"({', '.join(invalid_codepoints)}). Se muestra solo el código Unicode, no el carácter ni el secret."
            )
        elif len(compact_secret) % 4 == 1:
            reason = "la longitud no puede corresponder a una cadena Base64 válida."
        else:
            reason = "la cadena tiene un relleno Base64 inválido o está incompleta."
        print(f"Resultado: {reason} No se envió ninguna petición a Kraken.")
        return 2

    payload = None
    http_error = None
    error_body = ""
    authent = ""
    authenticated_via = ""
    # Try the key-check operation path forms, then the standard, documented
    # Derivatives v3 accounts endpoint as a read-only authentication fallback.
    candidates = (
        (BASE_URL + API_BASE_PATH + ENDPOINT_PATH, ENDPOINT_PATH, "key-check"),
        (BASE_URL + API_BASE_PATH + ENDPOINT_PATH, API_BASE_PATH + ENDPOINT_PATH, "key-check"),
        (BASE_URL + "/derivatives/api/v3/accounts", "/api/v3/accounts", "accounts"),
    )
    for attempt, (request_url, signing_path, method_name) in enumerate(candidates):
        authent = _authent(api_secret, signing_path)
        request = Request(
            request_url,
            headers={
                "apikey": api_key,
                "authent": authent,
                "Accept": "application/json",
                "User-Agent": STANDARD_USER_AGENT,
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
            authenticated_via = method_name
            if method_name == "accounts" and payload.get("result") != "success":
                safe_error = payload.get("error") or payload.get("result") or "respuesta inesperada"
                print(f"Resultado: Kraken contestó al endpoint de cuentas, pero no confirmó acceso ({safe_error}).")
                return 1
            break
        except HTTPError as exc:
            error_body = exc.read(4096).decode("utf-8", errors="replace")
            try:
                error_payload = json.loads(error_body)
            except json.JSONDecodeError:
                error_payload = {}
            if (
                attempt < len(candidates) - 1
                and exc.code == 401
                and error_payload.get("error") == "request_signature_invalid"
            ):
                continue
            http_error = exc
            break
        except (URLError, TimeoutError, OSError):
            print("Resultado: no se pudo alcanzar Kraken; comprueba la conexión e inténtalo de nuevo.")
            return 1
        except (UnicodeDecodeError, json.JSONDecodeError):
            print("Resultado: Kraken respondió con un formato inesperado.")
            return 1

    if http_error is not None:
        exc = http_error
        if exc.code == 401:
            try:
                error_payload = json.loads(error_body)
                parts = [
                    error_payload.get(field)
                    for field in ("error", "message", "suberror")
                    if isinstance(error_payload.get(field), str) and error_payload.get(field)
                ]
                detail = "; ".join(parts) if parts else "Kraken no incluyó un detalle legible."
            except json.JSONDecodeError:
                detail = "Kraken devolvió un cuerpo no JSON."
            detail = detail.replace(api_key, "[API key ocultada]").replace(authent, "[firma ocultada]")
            print(
                "Resultado: Kraken no autenticó esta clave en el endpoint de Derivatives. "
                f"Detalle de Kraken: {detail}"
            )
        elif exc.code == 400:
            try:
                error_payload = json.loads(error_body)
                parts = [
                    error_payload.get(field)
                    for field in ("error", "message", "suberror")
                    if isinstance(error_payload.get(field), str) and error_payload.get(field)
                ]
                detail = "; ".join(parts) if parts else "Kraken no incluyó un detalle legible."
            except json.JSONDecodeError:
                detail = "Kraken devolvió un cuerpo no JSON; se omite para no mostrar datos inesperados."
            detail = detail.replace(api_key, "[API key ocultada]").replace(authent, "[firma ocultada]")
            server = exc.headers.get("Server", "no indicado")
            content_type = exc.headers.get("Content-Type", "no indicado")
            print(
                f"Resultado: HTTP 400. Detalle: {detail} "
                f"Servidor: {server}. Content-Type: {content_type}."
            )
        elif exc.code == 403:
            edge_server = (exc.headers.get("Server") or "").lower()
            cf_match = re.search(r"error code:\s*(\d+)", error_body, flags=re.IGNORECASE)
            if cf_match:
                detail = f"Cloudflare bloqueó la petición (código {cf_match.group(1)})."
            elif "cloudflare" in edge_server:
                detail = "La petición fue bloqueada en la capa Cloudflare antes de confirmar la API key."
            else:
                try:
                    error_payload = json.loads(error_body)
                    safe_error = error_payload.get("error") or error_payload.get("message")
                    detail = f"Respuesta de Kraken: {safe_error}" if isinstance(safe_error, str) else "Kraken bloqueó la petición."
                except json.JSONDecodeError:
                    detail = "Kraken o su protección perimetral bloqueó la petición."
            print(
                f"Resultado: HTTP 403. {detail} Esto no demuestra que el par de claves sea incorrecto. "
                "Si persiste con el User-Agent actualizado, no reintroduzcas las claves: contacta con soporte de Kraken."
            )
        else:
            print(f"Resultado: Kraken respondió HTTP {exc.code}; no se pudo confirmar la clave.")
        return 1

    if authenticated_via == "accounts":
        print("Resultado: Kraken autenticó la clave en el endpoint Derivatives accounts (solo lectura).")
        print("La respuesta de cuenta se descartó y no se mostró ni se guardó.")
    else:
        permissions = payload.get("permissions") or {}
        general = permissions.get("general", "no indicado")
        transfer = permissions.get("transfer", "no indicado")
        print("Resultado: clave autenticada por el endpoint de Kraken Derivatives.")
        print(f"Permiso general: {general}")
        print(f"Permiso de transferencias/retiros: {transfer}")
    print("No se muestran ni guardan la clave ni el secret.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nComprobación cancelada; no se realizó ninguna operación de trading.")
        raise SystemExit(130)
