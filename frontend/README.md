# OSCAR Terminal Frontend

Frontend React/Vite del dashboard HD-007 para la release candidate `1.0.0-rc1`.

## Comandos

- `npm run dev` inicia la UI en modo desarrollo.
- `npm run build` genera la build de producción.
- `npm run test` ejecuta las pruebas de render e integración.

## Instalacion

1. Instalar Node.js 20+.
2. Ejecutar `npm install` dentro de `frontend/`.
3. Levantar la UI con `npm run dev -- --host 127.0.0.1 --port 5173`.

## Contrato del dashboard

- Consume solo las APIs públicas existentes de `market`, `smart-money`, `journal`, `playbook`, `analytics` y `health`.
- El chart engine existente se mantiene sin cambios funcionales.
- Los estados vacíos y de carga se renderizan directamente en la UI para no inventar datos.
- El cliente Axios apunta a `http://127.0.0.1:8000/api/v1`, por lo que `getHealth()` usa el contrato versionado `/api/v1/health`; el launcher operativo verifica además `GET /health` en raíz.

## Estructura

- `src/api`: tipos y clientes HTTP del dashboard.
- `src/components`: bloques visuales reutilizables y chart.
- `src/pages/Dashboard.tsx`: integración del flujo completo expuesto en UI.
- `src/test` y `src/pages/*.test.tsx`: pruebas de integración del dashboard.

## Notas de implementación

- La vista está diseñada como terminal institucional oscura y responsive.
- El panel de health muestra el contrato público disponible por API y el flujo de datos visible del frontend.
- No se ha tocado backend ni lógica de negocio.