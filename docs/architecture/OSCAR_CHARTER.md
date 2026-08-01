# PROYECTO

====================================================

OSCAR Terminal

Institutional Trading Operating System (ITOS)

## MISION

Transformar la metodologia de trading institucional en un
sistema de decision totalmente explicable, deterministico y testeable.

## PRINCIPIOS ARQUITECTONICOS

1. Principio de Responsabilidad Unica.
2. Los motores de decision nunca conocen la UI.
3. La UI consume TradePlan.
4. Todo motor devuelve EngineResult.
5. Toda decision debe ser explicable.
6. Toda regla debe ser testeable.
7. Sin logica de trading duplicada.
8. La metodologia guia la implementacion.

La implementacion nunca guia la metodologia.

## ESTANDAR DE CALIDAD

Todo Epic debe finalizar con:

- ✔ Unit Tests
- ✔ Documentacion
- ✔ Build
- ✔ Arquitectura Limpia
- ✔ Commit

## DEFINITION OF DONE

The Epic is completed ONLY IF:

- Decision Framework is generic.
- No trading logic exists.
- Every class has one responsibility.
- 100% typed.
- Documented.
- Unit tested.
- pytest passes.
- npm build passes.
- Ready for future engines.
- No frontend modifications.
- No Dashboard modifications.
- No Scanner modifications.

## NON GOALS

This Epic MUST NOT:

- Implement trading logic.
- Implement Context Engine.
- Implement MSS Engine.
- Implement Entry Engine.
- Implement Pipeline.
- Modify UI.
- Modify MT5 integration.

Only create the reusable framework.

## FUTURE INTEGRATION

The framework must support:

- Liquidity Engine
- Premium Discount Engine
- Structure Engine
- Context Engine
- MSS Engine
- IEZ Engine
- Entry Engine
- Trade Management Engine
- Institutional Trade Pipeline
- Decision Center
- Explainable AI
- Journal
- Replay Mode
