# OSCAR Trade IA

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

## Endpoints

- `POST /api/v1/decision/report`
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

## Notas

- La ejecución usa MetaTrader 5 directamente.
- Las pruebas mockean completamente MT5.
- El analisis del Decision Center es deterministico y derivado de datos existentes.