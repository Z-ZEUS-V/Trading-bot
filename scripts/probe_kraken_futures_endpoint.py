"""Probe the Kraken Futures key-check endpoint without sending credentials."""

from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL = "https://futures.kraken.com/api/auth/v1/api-keys/v3/check"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def main() -> int:
    print("Prueba de conectividad Kraken Futures; no envía claves ni puede operar.")
    request = Request(URL, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=15) as response:
            status = response.status
            headers = response.headers
            body = response.read(512).decode("utf-8", errors="replace")
    except HTTPError as exc:
        status = exc.code
        headers = exc.headers or {}
        body = exc.read(512).decode("utf-8", errors="replace")
    except (URLError, TimeoutError, OSError) as exc:
        print(f"No se pudo completar la conexión ({type(exc).__name__}).")
        return 1

    print(f"HTTP: {status}")
    print(f"Server: {headers.get('Server', 'no indicado')}")
    print(f"Content-Type: {headers.get('Content-Type', 'no indicado')}")
    excerpt = " ".join(body.split())[:300]
    print(f"Cuerpo (máx. 300 caracteres): {excerpt or '[vacío]'}")
    print("Respuesta esperable sin credenciales: HTTP 401 de la API de Kraken.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
