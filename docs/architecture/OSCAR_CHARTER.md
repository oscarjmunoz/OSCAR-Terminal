# OSCAR Trade IA Charter

## Objetivo

Publicar la release candidate `1.0.0-rc1` estabilizando el sistema existente sin introducir nuevas funcionalidades, nuevos motores ni cambios de arquitectura.

## Principios

1. Mantener contratos públicos estables salvo correcciones críticas de integración.
2. Priorizar validación extremo a extremo sobre expansión funcional.
3. Mantener el flujo institucional determinista y trazable.
4. Reutilizar módulos existentes sin duplicar lógica de negocio.
5. Favorecer errores coherentes y observabilidad suficiente para operación.
6. Eliminar solo código muerto, imports innecesarios y duplicación evidente.
7. Documentar el flujo real que hoy sostiene la release.
8. Liberar únicamente con pruebas automáticas y contratos operativos verificados.

## Flujo integral

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

## Responsabilidades por capa

- Market Engine: conectividad MT5, estado de terminal, ticks y velas.
- Institutional Pipeline: enriquecimiento de contexto institucional existente.
- Decision Center: genera `DecisionReport` sin ejecutar órdenes.
- Trading Journal: conserva snapshots del `DecisionReport` y trazabilidad del trader.
- Institutional Playbook: evalúa setups declarativos sobre journal y reportes.
- Performance Analytics: resume desempeño sin recalcular el pipeline institucional.
- Dashboard: visualiza únicamente contratos públicos ya expuestos.

## Contratos operativos de release

- Health raíz: `GET /health`
- Health versionado: `GET /api/v1/health`
- API pública: prefijo `/api/v1`
- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## Puertas de calidad

- `pytest` del backend en verde.
- Sin dependencias circulares detectadas en la composición principal.
- Flujo documentado desde mercado hasta dashboard.
- Documentación de instalación y estructura actualizada.
- Riesgos operativos explícitos antes de liberar.
