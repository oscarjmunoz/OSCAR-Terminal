# OSCAR Launcher v1.0

Launcher de un clic para iniciar y detener OSCAR Trade IA sin modificar modulos del sistema.

## Estructura

- `launcher/start_oscar.bat`: inicio con un clic.
- `launcher/stop_oscar.bat`: detiene backend y frontend iniciados por el launcher.
- `launcher/restart_oscar.bat`: reinicio (stop -> start).
- `launcher/start_oscar.py`: orquestador de arranque.
- `launcher/stop_oscar.py`: orquestador de parada.

## Como iniciar

1. Ejecutar `launcher/start_oscar.bat`.
2. El launcher valida Python, entorno virtual, Node, dependencias, backend y frontend.
3. Si todo esta correcto, abre `http://localhost:5173` automaticamente.

## Como detener

1. Ejecutar `launcher/stop_oscar.bat`.
2. Se cierran solo los procesos que el launcher haya iniciado (backend/frontend y su arbol).

## Como reiniciar

1. Ejecutar `launcher/restart_oscar.bat`.
2. Secuencia: stop -> start.

## Manejo de errores comunes

### Python no encontrado

- Mensaje: `[ERROR] Python was not found.`
- Solucion: instalar Python 3.12+ y volver a ejecutar.

### Node o npm no encontrados

- Mensaje: `[ERROR] Node.js / npm not found...`
- Solucion: instalar Node.js 20+.

### Dependencias backend faltantes

- Mensaje: `Backend dependencies missing.`
- Solucion: ejecutar `pip install -r backend/requirements.txt` con el Python usado por el launcher.

### Dependencias frontend faltantes

- Mensaje: `Frontend dependencies not installed.`
- Solucion: ejecutar `cd frontend && npm install`.

### Puerto 8000 o 5173 ocupado

- Mensaje: `Port 8000 is already in use...` o `Port 5173 is already in use...`
- Solucion: cerrar el proceso que ocupa el puerto y reintentar.

### Backend o frontend no listos dentro del timeout

- Mensaje: `did not become healthy in time` o `did not become available in time`.
- Solucion: revisar logs ejecutando backend/frontend manualmente para diagnostico.

## Nota operativa

El estado de procesos administrados se guarda en `launcher/oscar_launcher_state.json` para permitir una parada segura sin matar procesos ajenos.
