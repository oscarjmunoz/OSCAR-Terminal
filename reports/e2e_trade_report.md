# E2E Trade Validation Report

- Fecha: 2026-08-04T01:08:22.120691+00:00
- Broker: ACG Markets Limited
- Cuenta: 2631022
- Servidor: ACGMarkets-Main
- Simbolo: USDCHF.pro

## Resultados
- HEALTH: [PASS] overallStatus=HEALTHY
- BUY: [FAIL] open failed error=BrokerRejected message=AutoTrading disabled by server | latency_ms=10.90
- SELL: [FAIL] open failed error=BrokerRejected message=AutoTrading disabled by server | latency_ms=9.40
- MODIFY: [FAIL] buy=SKIPPED (Open failed) | sell=SKIPPED (Open failed)
- CLOSE: [FAIL] buy=SKIPPED (Open failed) | sell=SKIPPED (Open failed)
- PENDING: [FAIL] Pending creation failed: AutoTrading disabled by server
- ERRORS: [PASS] checks=invalid_volume=InvalidOrder; invalid_sl=InvalidOrder; market_closed=SKIPPED

- Latencia promedio: 10.15 ms
- Tiempo total: 0.07 s
- Resultado final: FAIL

## Detalle Tecnico

```json
{
  "HEALTH": {
    "status": "PASS",
    "details": "overallStatus=HEALTHY",
    "latency_ms": null,
    "ticket": null,
    "price": null
  },
  "BUY": {
    "status": "FAIL",
    "details": "open failed error=BrokerRejected message=AutoTrading disabled by server",
    "latency_ms": 10.900199999014148,
    "ticket": null,
    "price": null
  },
  "SELL": {
    "status": "FAIL",
    "details": "open failed error=BrokerRejected message=AutoTrading disabled by server",
    "latency_ms": 9.396999999808031,
    "ticket": null,
    "price": null
  },
  "MODIFY": {
    "status": "FAIL",
    "details": "buy=SKIPPED (Open failed) | sell=SKIPPED (Open failed)",
    "latency_ms": null,
    "ticket": null,
    "price": null
  },
  "CLOSE": {
    "status": "FAIL",
    "details": "buy=SKIPPED (Open failed) | sell=SKIPPED (Open failed)",
    "latency_ms": null,
    "ticket": null,
    "price": null
  },
  "PENDING": {
    "status": "FAIL",
    "details": "Pending creation failed: AutoTrading disabled by server",
    "latency_ms": null,
    "ticket": null,
    "price": null
  },
  "ERRORS": {
    "status": "PASS",
    "details": "checks=invalid_volume=InvalidOrder; invalid_sl=InvalidOrder; market_closed=SKIPPED",
    "latency_ms": null,
    "ticket": null,
    "price": null
  },
  "MT5_CONNECTION": {
    "status": "PASS",
    "details": "{\n  \"connected\": true,\n  \"trade_allowed\": true,\n  \"broker\": \"ACG Markets Limited\",\n  \"account\": 2631022,\n  \"server\": \"ACGMarkets-Main\"\n}",
    "latency_ms": null,
    "ticket": null,
    "price": null
  },
  "SYMBOL": {
    "status": "PASS",
    "details": "{\n  \"symbol\": \"USDCHF.pro\",\n  \"market_open\": true,\n  \"visible\": true,\n  \"trade_allowed\": true,\n  \"symbol_trade_enabled\": true,\n  \"trade_mode\": 4\n}",
    "latency_ms": null,
    "ticket": null,
    "price": null
  }
}
```
