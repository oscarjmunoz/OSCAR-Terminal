# Reubicacion de entornos virtuales de Python fuera del repositorio

Este proyecto detecta entornos virtuales dentro del repo en:

- `./.venv`
- `./backend/.venv`

No se deben borrar de forma destructiva. El objetivo es moverlos fuera del repo para reducir indexacion y consumo de RAM en VS Code.

## Ruta objetivo recomendada (Windows)

Usar una carpeta de entornos fuera del repo:

`D:\\.venvs\\oscar-terminal\\Scripts\\python.exe`

Configuraciones ya actualizadas en el proyecto apuntan a ese patron con rutas relativas:

- `${workspaceFolder}/../.venvs/oscar-terminal/Scripts/python.exe`
- `${workspaceFolder:<nombre>}/../../.venvs/oscar-terminal/Scripts/python.exe`

## Opcion A (recomendada): recrear entorno limpio fuera del repo

1. Crear carpeta externa de entornos:
   - `mkdir D:\\.venvs`
2. Crear el nuevo entorno:
   - `py -3 -m venv D:\\.venvs\\oscar-terminal`
3. Activar entorno:
   - `D:\\.venvs\\oscar-terminal\\Scripts\\activate`
4. Instalar dependencias backend:
   - `pip install -r backend\\requirements.txt`

## Opcion B: mover entorno existente sin borrarlo

1. Cerrar VS Code y cualquier terminal usando el entorno.
2. Mover carpeta:
   - desde `./backend/.venv` a `D:\\.venvs\\oscar-terminal`
   - o desde `./.venv` a `D:\\.venvs\\oscar-terminal`
3. Reabrir VS Code y confirmar interprete en Command Palette:
   - `Python: Select Interpreter`

## Verificacion

- Ejecutar tarea `Run Backend`.
- Ejecutar tarea `Run pytest`.
- Verificar que no queden errores de interprete en VS Code.

## Notas

- Si se mantiene temporalmente un `.venv` dentro del repo, ya esta excluido de indexacion, busqueda y file watchers.
- Evitar tener simultaneamente dos entornos (`./.venv` y `./backend/.venv`) para no confundir herramientas.
