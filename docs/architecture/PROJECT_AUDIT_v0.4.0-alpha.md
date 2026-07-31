# 1. Repository Structure

Resumen de estructura observada:

```text
OSCAR-Terminal/
  backend/
    app/
      api/
      config/
      core/
      database/
      market/
      models/
      schemas/
      services/
      smart_money/
    tests/
    run.py
    requirements.txt
  frontend/
    src/
      api/
      components/
      core/
      engine/
      layouts/
      pages/
    package.json
    vite.config.ts
    tsconfig.json
  launcher/
    launcher.py
    check_system.py
    config.py
    start_oscar.bat
    stop_oscar.bat
    restart_oscar.bat
    check_system.bat
  docs/
    architecture/
    roadmap/
    guides/
    api/
    diagrams/
    screenshots/
  README.md
  PRODUCT_VISION.md
  CHANGELOG.md
```

# 2. Backend

Modulos implementados y estado:

| Modulo          | Estado   | Observaciones                                                                                 |
| --------------- | -------- | --------------------------------------------------------------------------------------------- |
| app.main        | Complete | App FastAPI, CORS, root endpoint y health endpoint raiz.                                      |
| app.api         | Complete | Router general y endpoints de health/info/system.                                             |
| app.config      | Complete | Settings centralizados.                                                                       |
| app.core        | Complete | Logger base implementado.                                                                     |
| app.database    | Complete | Base ORM y session/engine configurados.                                                       |
| app.market      | Partial  | Routers, modelos y servicios presentes; requiere mayor cobertura de pruebas funcionales.      |
| app.smart_money | Partial  | Motores/servicios presentes; requiere cierre de integraciones visuales frontend relacionadas. |
| app.models      | Partial  | Modelo system_log presente; dominio de modelos aun acotado.                                   |
| app.schemas     | Planned  | Solo **init**.py, sin contratos expuestos en esta capa.                                       |
| app.services    | Planned  | Solo **init**.py, sin servicios agregados en esta carpeta.                                    |
| backend.tests   | Partial  | Test de health activo (2 tests), sin suite amplia por dominio.                                |

# 3. Frontend

Inventario y estado:

| Area         | Estado   | Detalle                                                                                                                                                   |
| ------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Components   | Partial  | TradingChart, SmartMoneyOverlay, LiquidityOverlay. Overlays con TODOs de compatibilidad API chart.                                                        |
| Layouts      | Complete | DecisionCenterLayout, Header, Sidebar, StatusBar.                                                                                                         |
| Pages        | Partial  | Dashboard principal implementado; no se observan paginas secundarias.                                                                                     |
| Hooks        | Planned  | No existe directorio frontend/src/hooks.                                                                                                                  |
| Services/API | Partial  | Cliente y adapters en frontend/src/api (client, market, smartMoney).                                                                                      |
| Core         | Complete | LiveDataOrchestrator y tipos compartidos presentes.                                                                                                       |
| Engine       | Partial  | Amplia base implementada (pipeline, strategy, decision, mtf, journal, analytics, validation, backtest), con pendientes de cierre UI y robustez operativa. |

# 4. Trading Engines

Estado por motor:

| Engine                 | Estado   | Observaciones                                                                     |
| ---------------------- | -------- | --------------------------------------------------------------------------------- |
| Institutional Pipeline | Complete | runInstitutionalPipeline implementado y testeado unitariamente.                   |
| Strategy Framework     | Complete | Strategy interface, ICTStrategy y StrategyRegistry activos.                       |
| Decision Engine        | Complete | Delegacion a estrategia activa implementada.                                      |
| Journal                | Partial  | JournalEngine/Repository implementados en memoria; sin persistencia externa.      |
| Analytics              | Partial  | AnalyticsEngine implementado; adopcion funcional en UI aun limitada.              |
| Validation             | Complete | ValidationEngine y tipos implementados y usados en Dashboard.                     |
| Backtest               | Complete | BacktestEngine con tests y resumen de metricas.                                   |
| Multi-Timeframe        | Partial  | Engine presente; madurez depende de integracion total en UX y flujos de decision. |

# 5. Launcher

Estado real:

| Elemento                      | Estado   | Observaciones                                                                                                             |
| ----------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------- |
| Python launcher (launcher.py) | Complete | Arranque backend, espera /health 200, arranque frontend, apertura navegador, stop/restart/check.                          |
| Batch wrappers                | Complete | BAT reducidos a wrappers Python (start/stop/restart/check).                                                               |
| check_system.py               | Partial  | Verifica Python/Node/npm/Git/backend/frontend/MT5; MT5 depende de deteccion local y puede quedar en WARN.                 |
| Pendientes                    | Partial  | Hay artefactos operativos versionados (.oscar_launcher_state.json y **pycache** en launcher), conviene excluirlos en VCS. |

# 6. Documentation

Documentos existentes relevantes:

- docs/architecture: arquitectura, engine, producto, guia UI, ADR-001..003.
- docs/roadmap: roadmap, changelog, release notes.
- docs/guides: install, development, contributing, git workflow.
- docs/api: backend y frontend API base.
- docs/diagrams: drawio placeholders + README.
- docs/screenshots: README + carpetas versionadas.

Documentos faltantes o incompletos:

- Guia de despliegue (staging/produccion).
- Politica de versionado semantico y release checklist formal.
- Guia de testing integral (frontend, backend, engines, e2e).
- Runbook de incidentes/operacion.
- Catalogo de endpoints backend con ejemplos request/response completos.

# 7. Technical Debt

Hallazgos:

- Frontend overlays deshabilitados temporalmente por compatibilidad con lightweight-charts:
  - frontend/src/components/SmartMoneyOverlay.tsx (TODO markers/price lines)
  - frontend/src/components/LiquidityOverlay.tsx (TODO liquidity lines)
- Warning de deprecacion en backend por uso de on_event (startup/shutdown) en FastAPI.
- Cobertura de tests limitada en backend (principalmente health).
- Artefactos de runtime/cache dentro del repo en launcher (state file y pycache trackeados).
- Estructura backend con carpetas placeholders (schemas/services) sin implementacion funcional.

Codigo duplicado (evaluacion):

- No se detecto duplicacion critica de logica de negocio en el muestreo auditado.
- Existe posible duplicidad documental de changelog (raiz y docs/roadmap), recomendable definir una fuente oficial.

# 8. Build Status

Estado observado durante la auditoria:

- Backend tests:
  - Comando: pytest tests/test_health.py -q
  - Resultado: PASS (2 passed)
  - Warnings: 5 (deprecaciones FastAPI/TestClient)

- Frontend build:
  - Comando: npm run build
  - Resultado: FAIL
  - Error: FATAL ERROR: Zone Allocation failed - process out of memory

Dependencias declaradas:

- Backend (requirements.txt): fastapi, uvicorn[standard], pydantic, pydantic-settings, python-dotenv, sqlalchemy, httpx, MetaTrader5, pytest.
- Frontend (package.json): react, react-dom, axios, lightweight-charts, lucide-react, zustand, vite, typescript, tailwind/postcss stack.

# 9. Recommendations

Top 10 prioridades:

1. Corregir fallo de build frontend por memoria (perfil de build, entorno Node, consumo de plugins).
2. Migrar eventos FastAPI on_event a lifespan handlers para eliminar deprecaciones.
3. Reactivar overlays Smart Money/Liquidity con API compatible de lightweight-charts.
4. Excluir artefactos operativos y caches del launcher del control de versiones.
5. Ampliar suite de pruebas backend por dominios market y smart_money.
6. Agregar pruebas de integracion frontend para pipeline/decision/dashboard.
7. Completar carpetas backend schemas/services o consolidarlas para evitar placeholders.
8. Definir una unica fuente oficial de changelog.
9. Expandir docs API con contratos y ejemplos completos por endpoint.
10. Crear runbook operativo para incidentes y troubleshooting de launcher/build.

# 10. Epic Status

| Epic                                 | Estado   | Version      |
| ------------------------------------ | -------- | ------------ |
| Decision Center                      | Complete | v0.4.0-alpha |
| Institutional Pipeline               | Complete | v0.4.0-alpha |
| Liquidity Engine                     | Complete | v0.4.0-alpha |
| Market Context Engine                | Complete | v0.4.0-alpha |
| Multi-Timeframe Engine               | Partial  | v0.4.0-alpha |
| Strategy Framework                   | Complete | v0.4.0-alpha |
| Validation Engine                    | Complete | v0.4.0-alpha |
| Backtest Engine                      | Complete | v0.4.0-alpha |
| Journal Engine                       | Partial  | v0.4.0-alpha |
| Performance Analytics Engine         | Partial  | v0.4.0-alpha |
| Python Launcher                      | Complete | v0.4.0-alpha |
| Smart Money Visual Engine (overlays) | Partial  | v0.4.0-alpha |
