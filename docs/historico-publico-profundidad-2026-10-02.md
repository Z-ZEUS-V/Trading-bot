# Profundidad del histórico público de Kraken Derivatives

**Fecha de captura:** 2 de octubre de 2026 (UTC)

**Uso:** preparar y auditar el conjunto de datos para investigación y backtests; no es una recomendación de trading.

## Método y límite de las consultas

Se usó el snapshot público del catálogo `data/market_data/instruments/20261002T001640Z/response.json` y el filtro de 172 contratos cripto perpetuos descrito en su manifiesto. Para cada contrato se consultó `trade`, `mark`, `funding` y `future-basis` desde `openingDate` hasta la captura: 688 peticiones, sin credenciales ni órdenes. Respuestas, primeras/últimas marcas, cantidad, flag de truncamiento y SHA-256 están en `data/market_data/history_depth/20261002T010323Z/depth.json`.

Las respuestas de intervalo completo llegaron a 2.000 puntos y avisaron que había más páginas para 169–170 contratos por serie. Así que el primer punto observado permite estimar la antigüedad alcanzable, pero esa llamada por sí sola no entrega el histórico entero ni prueba continuidad. Para las velas, mark y basis, la fecha inicial varía por instrumento. Funding solo mostró historia desde febrero de 2026 en este sondeo. El catálogo es el universo actual observado, no una reconstrucción punto-en-tiempo: hay sesgo de supervivencia si se usa para un backtest transversal.

| Serie | Contratos con datos | Punto más antiguo observado | Mediana de antigüedad observada | Máximo de antigüedad observada | Respuestas truncadas |
|---|---:|---|---:|---:|---:|
| Trade candles | 172/172 | 2020-02-26 | 903 días | 2.410 días | 170 |
| Mark candles | 172/172 | 2021-07-07 | 903 días | 1.912 días | 170 |
| Funding | 172/172 | 2026-02-12 | 231 días | 231 días | 169 |
| Future basis | 172/172 | 2021-07-07 | 903 días | 1.912 días | 170 |

Antigüedad común estimada entre las cuatro series: 169 contratos alcanzan al menos 90 días; ninguno alcanza 365 días. Dos contratos de la instantánea actual tienen menos de 30 días de observaciones comunes. Son límites de disponibilidad aproximados calculados desde las primeras marcas devueltas, no prueba de que las 4 series estén alineadas o completas durante todo ese periodo.

## Conjunto histórico descargado para BTC/ETH

Para disponer de una base sin el límite de puntos por respuesta, se ingirieron `PF_XBTUSD` y `PF_ETHUSD` en ventanas de 30 días. Los ficheros versionados están en `data/market_data/datasets/20261002T010411Z/`: 8 CSV gzip normalizados, respuestas originales comprimidas por ventana y un `manifest.json` con metadatos, SHA-256, consultas y huecos.

| Contrato / serie | Puntos | Desde (UTC) | Hasta (UTC) | Huecos horarios | Errores de consulta |
|---|---:|---|---|---:|---:|
| PF_XBTUSD trade | 39.688 | 2022-03-23 10:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_XBTUSD mark | 39.709 | 2022-03-22 13:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_XBTUSD funding | 5.557 | 2026-02-12 13:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_XBTUSD future-basis | 39.709 | 2022-03-22 13:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_ETHUSD trade | 39.688 | 2022-03-23 10:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_ETHUSD mark | 39.709 | 2022-03-22 13:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_ETHUSD funding | 5.557 | 2026-02-12 13:00 | 2026-10-02 01:00 | 0 | 0 |
| PF_ETHUSD future-basis | 39.709 | 2022-03-22 13:00 | 2026-10-02 01:00 | 0 | 0 |

El dataset cubre aproximadamente 4,5 años de trade/mark/basis para los dos perpetuos lineales y unos 7,5 meses de funding. **No se rellenó ni interpoló funding antes de su primera observación.** Una estrategia que dependa de funding no puede evaluarse honestamente durante el tramo anterior sin otra fuente verificada. Los saltos mayores de una hora son cero en los manifiestos; esto no reemplaza revisar las reglas de timestamp, publicación del funding y valor económico de cada campo.

## Uso en backtest y límites

- BTC y ETH son el conjunto técnico inicial por historia común amplia y por permitir verificar el motor; esto no los convierte en la shortlist final ni confirma acceso de la cuenta.
- Descargar las ventanas pequeñas es necesario para sortear el tope de 2.000 puntos de una petición larga. El script `scripts/ingest_kraken_public_history.py` guarda tanto respuestas como datos normalizados.
- Usar el dataset versionado y su hash; no modificar las fuentes comprimidas. Mantener las ejecuciones futuras en directorios nuevos.
- Tratar funding anterior al primer punto como ausente (`null`/sin observación), nunca como cero. Aplicar los pagos solo con la convención temporal y del contrato confirmada.
- Aún no hay backtest implementado ni resultados de rentabilidad. Antes de comparar estrategias hacen falta costes, slippage, spread, especificaciones y reglas fijadas de antemano; tampoco existe aún un universo histórico libre de sesgo de supervivencia.
- La autenticación privada continúa en espera de Kraken Support. Todo lo anterior es lectura de datos públicos.
