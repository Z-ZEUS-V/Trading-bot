"""Capture Kraken Derivatives' public instrument catalog without credentials."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CATALOG_URL = "https://futures.kraken.com/derivatives/api/v3/instruments"
USER_AGENT = "AstraTradingResearch/0.1 (public market-data research)"
TIMEOUT_SECONDS = 30


def capture(output_root: Path) -> Path:
    request = Request(
        CATALOG_URL,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            raw = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"Kraken respondió HTTP {exc.code} al pedir el catálogo público.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("No se pudo alcanzar el endpoint público de instrumentos de Kraken.") from exc

    if status != 200:
        raise RuntimeError(f"Respuesta HTTP inesperada: {status}.")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Kraken devolvió una respuesta que no es JSON válido.") from exc
    instruments = payload.get("instruments")
    if not isinstance(instruments, list):
        raise RuntimeError("La respuesta no contiene la lista 'instruments' esperada.")

    captured_at = datetime.now(UTC)
    capture_id = captured_at.strftime("%Y%m%dT%H%M%SZ")
    capture_dir = output_root / "instruments" / capture_id
    capture_dir.mkdir(parents=True, exist_ok=False)
    raw_path = capture_dir / "response.json"
    raw_path.write_bytes(raw)

    symbols = [item.get("symbol") for item in instruments if isinstance(item, dict)]
    manifest = {
        "captured_at_utc": captured_at.isoformat(timespec="seconds"),
        "source": CATALOG_URL,
        "http_status": status,
        "content_type": content_type,
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "response_file": raw_path.name,
        "instrument_count": len(instruments),
        "server_time": payload.get("serverTime"),
        "filters_applied": [],
        "notes": [
            "Snapshot completo de la respuesta pública; no implica elegibilidad de la cuenta.",
            "No se han inferido mercados cripto/perpetuos ni se han eliminado instrumentos.",
        ],
        "symbols": symbols,
    }
    (capture_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return capture_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guarda una instantánea fechada del catálogo público de Kraken Derivatives."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/market_data"),
        help="Directorio raíz de instantáneas (por defecto: data/market_data).",
    )
    args = parser.parse_args()
    try:
        capture_dir = capture(args.output_dir)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    manifest = json.loads((capture_dir / "manifest.json").read_text(encoding="utf-8"))
    print(f"Catálogo capturado: {capture_dir}")
    print(f"Instrumentos: {manifest['instrument_count']}")
    print(f"serverTime: {manifest['server_time']}")
    print(f"SHA-256: {manifest['response_sha256']}")
    print("Sin API key; sin filtros; no se consultó ninguna cuenta ni se enviaron órdenes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
