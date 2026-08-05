# OSCAR Trade IA

Release candidate actual: `1.0.0-rc1`.

## Resumen

OSCAR integra los módulos existentes de mercado, contexto institucional, decisión, journal, playbook, analytics y dashboard sin introducir nuevos motores ni alterar la arquitectura vigente.

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

## Arquitectura

- `backend/`: API FastAPI, servicios, contratos, motores existentes y pruebas.
- `frontend/`: dashboard React/Vite que consume exclusivamente APIs públicas existentes.
- `database/`: artefactos SQLite locales.
- `scripts/`: validaciones operativas y utilidades de integración.
- `reports/`: evidencia de ejecuciones E2E y auditorías.

La referencia de arquitectura se documenta en `docs/architecture/OSCAR_CHARTER.md`.

## Instalacion

### Backend

1. Crear o activar un entorno virtual con Python 3.12.
2. Ejecutar `pip install -r backend/requirements.txt`.
3. Iniciar el servicio con `python backend/run.py`.
4. Validar `GET /health` en `http://127.0.0.1:8000/health`.

### Frontend

1. Instalar Node.js 20+.
2. Ejecutar `npm install` dentro de `frontend/`.
3. Iniciar la UI con `npm run dev -- --host 127.0.0.1 --port 5173`.

## Contratos operativos

- Launcher y monitoreo: `GET /health`
- Frontend versionado: `GET /api/v1/health`
- API pública: prefijo `http://127.0.0.1:8000/api/v1`

## Estado RC

- Backend con pruebas automáticas en verde.
- Dashboard integrado contra las APIs existentes.
- La validación E2E real con broker depende de que AutoTrading esté habilitado en el servidor MT5.
