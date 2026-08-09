# OSCAR Trade IA Backend

Release candidate actual: `1.0.0-rc1`.

## Instalacion

1. Crear o activar un entorno virtual de Python 3.12.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Ejecutar el backend desde `backend/` con `python run.py`.
4. Verificar contratos operativos en `http://127.0.0.1:8000/health` y `http://127.0.0.1:8000/api/v1/health`.

## Flujo completo

```text
Market Engine
	-> Institutional Pipeline
	-> Decision Center
	-> DecisionReport
	-> Trading Journal
	-> Institutional Playbook
	-> Performance Analytics
	-> Dashboard
```

## Flujo de ejecución

1. `InstitutionalPipeline` produce un `DecisionContext` con símbolo, lado, volumen, SL y TP.
2. `DecisionCenter` consume el `DecisionContext` y genera un `DecisionReport` institucional completo (sin ejecutar ordenes).
2. `TradeExecutor` recibe la confirmación del usuario y delega en `OrderBuilder`.
3. `OrderValidator` comprueba mercado, símbolo, volumen, SL, TP y margen antes de enviar.
4. `TradeExecutionService` envía la orden a MetaTrader 5.
5. `TradeResult` devuelve el resultado tipado con ticket, precio, volumen, SL, TP, mensaje del broker, latencia y error.

## Decision Center v1.0

`DecisionCenter` reutiliza `DecisionContext`, `MarketService` y `SmartMoneyService` para construir un `DecisionReport` deterministico con:

- Market Bias
- Institutional Score (score, confidence, quality)
- Liquidity (buy, sell, taken, pending)
- Market Structure (trend, BOS, CHOCH, MSS)
- Institutional Zones (Order Block, Breaker, Mitigation, FVG, Premium, Discount)
- Confluences (detectada/no detectada/importancia)
- Risk Assessment (RR esperado, riesgo, volatilidad, calidad)
- Execution Checklist
- Final Recommendation (BUY, SELL, WAIT, NO TRADE)
- Narrative profesional

El Decision Center no automatiza trading y no envia ordenes.

## Trading Journal Inteligente

El Journal consume un `DecisionReport` ya generado y lo persiste en memoria sin recalcular analisis institucional ni depender de una base de datos.

HD-016B: el estado de paper positions es session-scoped in memory. No se agrega persistencia durable ni cambios de esquema en esta fase.

Flujo:

1. El usuario recibe un `DecisionReport` desde `DecisionCenter`.
2. El Journal guarda un `JournalEntry` con snapshot completo del `DecisionReport`.
3. El trader registra su decision: `FOLLOWED_OSCAR`, `IGNORED_OSCAR`, `WAITED` o `CANCELLED`.
4. El resultado del trade se actualiza posteriormente con `PENDING`, `WIN`, `LOSS`, `BREAK_EVEN` o `CANCELLED`.
5. Se pueden añadir notas personales, tags, busquedas y filtros sin tocar el pipeline institucional.

Endpoints:

- `POST /api/v1/journal`
- `GET /api/v1/journal`
- `GET /api/v1/journal/{id}`
- `PATCH /api/v1/journal/{id}`
- `DELETE /api/v1/journal/{id}`

## Institutional Playbook

El Institutional Playbook consume exclusivamente `DecisionReport` y `JournalEntry`.

Flujo:

1. `DecisionReport` alimenta el evaluador de setups institucionales.
2. `JournalEntry` conserva el snapshot del `DecisionReport` para evaluar historial sin recalcular analisis.
3. El Playbook compara reglas declarativas contra el report o contra los snapshots del Journal.
4. Se generan matches deterministicos, porcentaje de encaje y estadisticas historicas por setup.

Endpoints:

- `POST /api/v1/playbook`
- `GET /api/v1/playbook`
- `GET /api/v1/playbook/{id}`
- `PATCH /api/v1/playbook/{id}`
- `DELETE /api/v1/playbook/{id}`
- `POST /api/v1/playbook/evaluate`
- `GET /api/v1/playbook/statistics`

## Performance Analytics

Performance Analytics (HD-006) consume exclusivamente `JournalEntry`, el snapshot embebido de `DecisionReport` y las estadisticas del Playbook. No recalcula analisis institucional ni modifica los contratos del pipeline.

Flujo:

1. `DecisionReport` se congela como snapshot dentro de `JournalEntry`.
2. `Trading Journal` conserva decision, resultado, duracion y RR realizado.
3. `Playbook` aporta estadisticas historicas por setup.
4. `Performance Analytics` cruza esas fuentes para producir metricas deterministicas de resumen, sesiones, timeframes, simbolos, setups, recomendaciones OSCAR, confluencias y riesgo.

Diagrama:

```text
Journal
	|
	v
Analytics
	|
	v
Dashboard
```

Metricas implementadas:

- Summary: totalTrades, wins, losses, breakEven, cancelled, winRate, averageRR, averageProfit, averageLoss, expectancy, profitFactor.
- Session Analytics: Asia, London y New York con trades, winRate, averageRR y averageDuration.
- Timeframe Analytics: M1, M5, M15, H1 y H4.
- Symbol Analytics: agregacion por simbolo.
- Playbook Analytics: total trades, win rate, RR promedio y expectancy por setup.
- Oscar Recommendation Analytics: FOLLOWED_OSCAR, IGNORED_OSCAR, WAITED y CANCELLED con winRate, averageRR y profitFactor.
- Confluence Analytics: confluencias mas frecuentes en operaciones ganadoras.
- Risk Analytics: riesgo promedio, RR esperado vs alcanzado, drawdown maximo, mejor racha y peor racha.

Endpoints:

- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/sessions`
- `GET /api/v1/analytics/timeframes`
- `GET /api/v1/analytics/symbols`
- `GET /api/v1/analytics/playbook`
- `GET /api/v1/analytics/recommendations`
- `GET /api/v1/analytics/confluences`
- `GET /api/v1/analytics/risk`

## Endpoints

- `GET /health`
- `GET /api/v1/health`

- `POST /api/v1/decision/report`
- `POST /api/v1/paper/positions/{position_id}/update`
- `POST /api/v1/paper/positions/{position_id}/close`
- `POST /api/v1/journal`
- `GET /api/v1/journal`
- `GET /api/v1/journal/{id}`
- `PATCH /api/v1/journal/{id}`
- `DELETE /api/v1/journal/{id}`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/sessions`
- `GET /api/v1/analytics/timeframes`
- `GET /api/v1/analytics/symbols`
- `GET /api/v1/analytics/playbook`
- `GET /api/v1/analytics/recommendations`
- `GET /api/v1/analytics/confluences`
- `GET /api/v1/analytics/risk`
- `POST /api/v1/trade/buy`
- `POST /api/v1/trade/sell`
- `POST /api/v1/trade/close`
- `POST /api/v1/trade/modify/sl`
- `POST /api/v1/trade/modify/tp`
- `POST /api/v1/trade/cancel`

## Configuración

- `maxSlippage`
- `magicNumber`
- `defaultDeviation`

## Estructura

- `app/api`: contratos HTTP públicos y composición de routers.
- `app/services`: orquestación de ejecución, validaciones y health.
- `app/market`, `app/smart_money`, `app/engines`: lectura y enriquecimiento de contexto de mercado.
- `app/journal`, `app/playbook`, `app/analytics`: persistencia en memoria, evaluación y reporting.
- `tests`: regresión del backend y validación del flujo existente.

## Notas

- La ejecución usa MetaTrader 5 directamente.
- Las pruebas mockean completamente MT5.
- El analisis del Decision Center es deterministico y derivado de datos existentes.
- El endpoint raíz `/health` existe para el launcher y monitoreo operativo; el frontend sigue consumiendo `/api/v1/health` vía su `baseURL`.