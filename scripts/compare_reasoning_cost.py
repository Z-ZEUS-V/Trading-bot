from __future__ import annotations

import json
import os
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
AGENT_FILE = ROOT / "data" / "platform_agents.json"
EVIDENCE_FILE = ROOT / "data" / "research_runs" / "astra-strategy-evidence-20261001T193242Z.md"
EXCLUDED = {"short-volatility-premium", "execution-vwap-twap"}
INPUT_PRICE = 10.0
CACHED_INPUT_PRICE = 1.0
OUTPUT_PRICE = 50.0
HISTORICAL_MEDIUM_SESSION_ID = "sess_0870f6501a17db48006abeba080650819995880878f81c94b7"


def cost_usd(usage: dict) -> float:
    input_tokens = usage["input_tokens"]
    cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
    output_tokens = usage["output_tokens"]
    return ((input_tokens - cached) * INPUT_PRICE + cached * CACHED_INPUT_PRICE + output_tokens * OUTPUT_PRICE) / 1_000_000


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Astra reasoning levels with identical research input and record API usage.")
    parser.add_argument("--medium-session-id", help="Reuse a completed medium session with this exact comparison prompt.")
    parser.add_argument("--high-session-id", help="Reuse a completed high session with this exact comparison prompt.")
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY no está configurada en el entorno.")
    ids = json.loads(AGENT_FILE.read_text(encoding="utf-8"))
    agent_id = ids["astra_coordinator"]["id"]
    catalog = json.loads((ROOT / "data" / "strategies.json").read_text(encoding="utf-8"))
    candidates = [item for item in catalog if item["id"] not in EXCLUDED]
    evidence = EVIDENCE_FILE.read_text(encoding="utf-8")[:16000]
    fields = ("id", "name", "mechanism", "benefit_potential", "market_risk", "tail_risk", "implementation_risk", "cost_sensitivity", "evidence_strength", "capital_and_infrastructure", "failure_modes", "evidence_summary", "sources")
    packet = [{key: item[key] for key in fields if key in item} for item in candidates]
    prompt = (
        "MODO RESEARCH_SELECTION. Compara las ocho candidatas incluidas usando las fichas y el informe de evidencia adjunto. "
        "Objetivo: seleccionar hipótesis para investigación y backtests, no aprobar operativa. No presupongas exchange, venue ni contrato; "
        "el usuario lo especificará cuando comience la fase de creación. Evalúa calidad y correspondencia de evidencia, robustez fuera de muestra "
        "y por régimen, costes netos, drawdown y colas, liquidez, datos e implementación. Ordena las ocho, selecciona hasta cuatro para backtests "
        "comparables y señala una primera prioridad. Explica riesgos materiales y qué evidencia cambiaría el ranking. Distingue evidencia publicada, "
        "inferencias, resultados brutos/netos y ausencia de validación; no inventes resultados ni hagas decisión de mercado en vivo. Responde en español, "
        "Markdown conciso pero suficientemente detallado para comparar. Usa las referencias provistas; no hagas una búsqueda nueva.\n\n"
        "Fichas de candidatas:\n" + json.dumps(packet, ensure_ascii=False) + "\n\nInforme de evidencia (idéntico para ambas ejecuciones):\n" + evidence
    )
    results = {}
    with OpenAI() as client:
        def recover_session(session_id: str) -> tuple[str, dict]:
            session = client.beta.agents.sessions.retrieve(session_id)
            page = client.beta.agents.sessions.items.list(session_id, limit=100, order="asc")
            recovered_text = "".join(
                part.text
                for item in page.data
                if item.type == "message" and item.role == "assistant"
                for part in item.content
                if getattr(part, "text", None)
            )
            if not recovered_text or session.usage is None:
                raise RuntimeError(f"La sesión {session_id} no contiene respuesta completa y usage registrado.")
            return recovered_text, session.usage.model_dump()

        if args.medium_session_id:
            medium_text, medium_usage = recover_session(args.medium_session_id)
            results["medium"] = {"text": medium_text, "usage": medium_usage, "cost_usd": cost_usd(medium_usage), "session_id": args.medium_session_id}
        if args.high_session_id:
            high_text, high_usage = recover_session(args.high_session_id)
            results["high"] = {"text": high_text, "usage": high_usage, "cost_usd": cost_usd(high_usage), "session_id": args.high_session_id}
        efforts = tuple(effort for effort in ("medium", "high") if effort not in results)
        for effort in efforts:
            output: list[str] = []
            session_id = None
            with client.beta.agents.sessions.create(
                agent_id=agent_id,
                agent={"reasoning": {"effort": effort}},
                environment={"type": "none"},
                input=prompt,
                stream=True,
            ) as events:
                completed = False
                for event in events:
                    if event.type == "agent.session.turn.output_text.delta":
                        output.append(event.delta)
                    elif event.type == "agent.session.turn.failed":
                        raise RuntimeError(f"{effort} falló: {event.turn.error.message if event.turn.error else 'error desconocido'}")
                    elif event.type == "agent.session.turn.cancelled":
                        raise RuntimeError(f"Ejecución {effort} cancelada.")
                    elif event.type == "agent.session.turn.completed" and event.turn.subagent_id is None:
                        completed = True
                        session_id = event.session_id
                if not completed:
                    raise RuntimeError(f"El stream {effort} terminó antes del evento de finalización.")
            print(f"[{effort}] sesión completada: {session_id}")
            session = client.beta.agents.sessions.retrieve(session_id)
            raw_usage = session.usage
            usage = raw_usage.model_dump() if raw_usage else None
            if usage is None:
                raise RuntimeError(f"La API no devolvió usage para {effort}; no se puede calcular el coste exacto de tokens.")
            results[effort] = {"text": "".join(output), "usage": usage, "cost_usd": cost_usd(usage), "session_id": session_id}
        historical_session = client.beta.agents.sessions.retrieve(HISTORICAL_MEDIUM_SESSION_ID)
        historical_usage = historical_session.usage.model_dump() if historical_session.usage else None
        if historical_usage is None:
            raise RuntimeError("No se pudo recuperar el usage de la selección medium original.")
        historical_medium = {"session_id": HISTORICAL_MEDIUM_SESSION_ID, "created_at": historical_session.created_at, "usage": historical_usage, "cost_usd": cost_usd(historical_usage)}

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_dir = ROOT / "data" / "research_runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    report_path = runs_dir / f"astra-reasoning-cost-comparison-{timestamp}.md"
    data_path = runs_dir / f"astra-reasoning-cost-comparison-{timestamp}.json"
    for effort in results:
        results[effort]["report_file"] = f"astra-reasoning-cost-comparison-{timestamp}-{effort}.md"
        (runs_dir / results[effort]["report_file"]).write_text(results[effort]["text"], encoding="utf-8")
    summary = {
        "timestamp_utc": timestamp,
        "model": "gpt-6-astra",
        "persistent_agent_reasoning_effort": "medium",
        "comparison_efforts": ["medium", "high"],
        "prompt_identical": True,
        "candidate_ids": [item["id"] for item in candidates],
        "evidence_file": str(EVIDENCE_FILE.relative_to(ROOT)).replace("\\", "/"),
        "rates_usd_per_million_tokens": {"uncached_input": INPUT_PRICE, "cached_input": CACHED_INPUT_PRICE, "output_including_reasoning": OUTPUT_PRICE},
        "historical_original_medium": historical_medium,
        "runs": {effort: {k: v for k, v in data.items() if k != "text"} for effort, data in results.items()},
    }
    data_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    med = results["medium"]
    high = results["high"]
    delta = high["cost_usd"] - med["cost_usd"]
    percent = (delta / med["cost_usd"] * 100) if med["cost_usd"] else None
    ranking = lambda text: re.search(r"(?is)(?:ranking completo|ranking)(.*?)(?:cuatro prioridades|prioridades para backtest|por qu[eé] posponer|$)", text).group(1).strip() if re.search(r"(?is)(?:ranking completo|ranking)(.*?)(?:cuatro prioridades|prioridades para backtest|por qu[eé] posponer|$)", text) else "No se pudo extraer automáticamente; consulte ambos informes completos."
    report = f"""# Comparación de coste: Astra medium frente a high

**Fecha UTC:** {timestamp}
**Modelo:** GPT-6 Astra (`{agent_id}`)
**Agente persistente:** permanece en `medium`; `high` se aplicó solo a esta sesión.
**Método:** mismo prompt, ocho fichas y mismo informe de evidencia para la comparación directa medium/high; sin búsqueda web durante las ejecuciones. Además, se recuperó el uso facturado de la selección medium original.
## Resumen de uso y coste

| Métrica | Medium | High | Diferencia high − medium |
|---|---:|---:|---:|
| Tokens de entrada | {med['usage']['input_tokens']:,} | {high['usage']['input_tokens']:,} | {high['usage']['input_tokens'] - med['usage']['input_tokens']:+,} |
| Entrada en caché | {med['usage']['input_tokens_details']['cached_tokens']:,} | {high['usage']['input_tokens_details']['cached_tokens']:,} | {high['usage']['input_tokens_details']['cached_tokens'] - med['usage']['input_tokens_details']['cached_tokens']:+,} |
| Tokens de salida (incluye razonamiento) | {med['usage']['output_tokens']:,} | {high['usage']['output_tokens']:,} | {high['usage']['output_tokens'] - med['usage']['output_tokens']:+,} |
| De salida: razonamiento | {med['usage']['output_tokens_details']['reasoning_tokens']:,} | {high['usage']['output_tokens_details']['reasoning_tokens']:,} | {high['usage']['output_tokens_details']['reasoning_tokens'] - med['usage']['output_tokens_details']['reasoning_tokens']:+,} |
| Total de tokens | {med['usage']['total_tokens']:,} | {high['usage']['total_tokens']:,} | {high['usage']['total_tokens'] - med['usage']['total_tokens']:+,} |
| **Coste estimado USD** | **${med['cost_usd']:.6f}** | **${high['cost_usd']:.6f}** | **${delta:+.6f} ({percent:+.1f}%)** |

La selección `medium` original, ejecutada a las 19:52 UTC, costó **${historical_medium['cost_usd']:.6f}** (entrada {historical_usage['input_tokens']:,}; salida {historical_usage['output_tokens']:,}; razonamiento {historical_usage['output_tokens_details']['reasoning_tokens']:,}). Se recuperó su usage directamente de la sesión de Agents API. Es un dato histórico; su prompt no es idéntico al par comparativo de arriba.

### Cálculo

`((entrada total − entrada cacheada) × $10 + entrada cacheada × $1 + salida × $50) / 1.000.000`. La salida incluye los tokens de razonamiento. Tarifas estándar publicadas para Astra: entrada $10/M, entrada cacheada $1/M y salida $50/M. No hay recargo separado por seleccionar `high`; el coste varía según tokens facturados. Ver [precios oficiales de GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).

## Comparación analítica

### Medium — extracto del ranking

{ranking(med['text'])}

### High — extracto del ranking

{ranking(high['text'])}

## Límites de esta medición

- El uso que reporta Agents API es best-effort; los costes son estimaciones calculadas sobre ese uso y las tarifas estándar publicadas, antes de ajustes de cuenta, impuestos o créditos. No se aplicaron descuentos de caché de escritura ni tarifas de servicio especial porque el registro de usage no desglosó esos componentes.
- El caché puede hacer que el coste de entrada cambie entre ejecuciones aunque el prompt sea idéntico; se reflejan los tokens cacheados medidos.
- La comparación contiene una ejecución por nivel; no mide variabilidad entre repeticiones ni prueba que cualquier diferencia del ranking venga solo del esfuerzo.
- La primera reevaluación guardó la respuesta en Markdown pero no el usage en el archivo; el usage histórico pudo recuperarse después desde Agents API. El medium de comparación y el high comparten prompt y paquete idénticos; sus session IDs están en el JSON adjunto.
- Los informes completos se guardan junto a este archivo como `...-medium.md` y `...-high.md`; los contadores brutos están en `astra-reasoning-cost-comparison-{timestamp}.json`.
"""
    report_path.write_text(report, encoding="utf-8")
    print(f"Saved comparison report: {report_path}")
    print(f"Saved raw usage data: {data_path}")
    print(f"Measured cost medium=${med['cost_usd']:.6f}; high=${high['cost_usd']:.6f}; delta=${delta:+.6f}")


if __name__ == "__main__":
    main()
