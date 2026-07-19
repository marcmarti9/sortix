# Sortix

Organizador automatico de descargas, con interfaz tipo explorador de
archivos. Vigila tu carpeta de Descargas y, en cuanto aparece un archivo
nuevo, lo mueve a la carpeta que le corresponde:

- **Fotos** -> `Pictures/Descargas`
- **Videos** -> `Videos/Descargas`
- **Musica** -> `Music/Descargas`
- **Comprimidos** -> `Downloads/Comprimidos`
- **Instaladores** (.exe, .msi, .deb, .apk...) -> `Downloads/Instaladores`
- **Cualquier otro documento** -> `Documents/Otros`
- **Todo lo demas** -> `Downloads/Otros`

Y ademas, **para absolutamente cualquier cosa que quieras agrupar** (no solo
la universidad: puede ser tu banco, el gimnasio, una app en concreto,
facturas de un proveedor...), defines **Temas**: un nombre, una carpeta
destino y unas palabras clave. Para los archivos PDF, DOCX y TXT, Sortix
mira primero el nombre del archivo y, si no hay pistas claras, el contenido
del documento buscando esas palabras clave. Si un documento no encaja con
ningun Tema, va a `Documents/Otros` en vez de forzarlo dentro de uno.

Ejemplo: creas el Tema "Banco" -> `Documents/Banco`, palabras clave
`banco, extracto, iban`. La primera vez que se descargue un PDF de tu banco,
Sortix crea la carpeta `Documents/Banco` sola y lo archiva ahi. Lo mismo
para "Gimnasio", "Netflix", o lo que sea que se te ocurra.

Tambien puedes crear reglas mas simples por extension (ej. `.log` ->
`Documents/Logs`), que siempre tienen prioridad sobre la clasificacion
automatica.

Todas las rutas son relativas a tu carpeta personal (`~` / `C:\Users\tu_usuario`),
asi que funciona igual en Linux, Windows y Mac.

## Como se usa

La idea es tocarlo una vez (crear tus Temas y reglas en Ajustes) y que a
partir de ahi corra solo en segundo plano. La interfaz principal es un
explorador de archivos: la barra lateral tiene Descargas, las categorias
base y tus Temas; al hacer click en cualquiera ves su contenido real, con
breadcrumbs para moverte entre carpetas. Arriba a la derecha: el interruptor
de **Patrulla Activa**, el boton **Organizar ahora** (para lo que ya haya en
Descargas), el selector de **idioma** (ES/EN), el interruptor de **tema claro/oscuro** (con animaciones de transición circulares) y el icono de engranaje para abrir **Ajustes** (Temas y reglas).

La primera vez que la abres, si no tienes ningun Tema ni regla, se abre
Ajustes solo para que definas los tuyos.

## Estructura del proyecto

```
backend/    servidor Python (Flask + watchdog) que vigila y organiza
frontend/   interfaz web (explorador de archivos) para gestionar Temas/reglas
database/   esquema y base de datos SQLite (temas, reglas, historial, ajustes)
```

## Uso manual (para probarlo)

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py
```

Abre http://127.0.0.1:5000 en el navegador.

Configuracion opcional en `backend/.env` (copia `backend/.env.example`):
`HOST`, `PORT`, `DOWNLOADS_DIR` (si tu carpeta de descargas no es la estandar).

## Instalar como servicio en segundo plano (recomendado)

Para que Sortix vigile Descargas siempre, sin tener que abrir nada a mano:

**Linux (systemd, servicio de usuario):**

```bash
cd backend/deploy
./install_linux.sh
```

Arranca con tu sesion y sigue corriendo en segundo plano. Para quitarlo:
`./uninstall_linux.sh`. Para que siga activo incluso sin sesion iniciada:
`sudo loginctl enable-linger $USER`.

**Windows (Tarea Programada, sin ventana):**

```powershell
cd backend\deploy
powershell -ExecutionPolicy Bypass -File install_windows.ps1
```

Para quitarlo: `powershell -ExecutionPolicy Bypass -File uninstall_windows.ps1`.

**macOS (LaunchDaemon, arranca con el sistema):**

```bash
cd backend/deploy
./install_macos.sh
```

Pide tu contrasena (sudo) porque se registra para arrancar con el propio
sistema, no solo al iniciar sesion. Para quitarlo: `./uninstall_macos.sh`.

En los tres casos, una vez instalado, sigue abriendo http://127.0.0.1:5000
cuando quieras encender/apagar la patrulla o tocar tus Temas/reglas — el
servicio de fondo se limita a escuchar ahi, no hace falta lanzar nada mas.

## Compartir con mas gente

El proyecto no tiene ninguna ruta ni usuario hardcodeado: cada persona que lo
clona y ejecuta el instalador de su sistema (Linux/Windows/macOS, arriba)
tiene su propia instalacion, con su propia base de datos, sus propios
Temas/reglas y vigilando su propia carpeta de Descargas. Nada se comparte
entre instalaciones.

Para que alguien lo use solo necesita:

```bash
git clone <la-url-de-tu-repo>
cd sortix/backend/deploy
./install_linux.sh   # o install_windows.ps1 / install_macos.sh segun su SO
```

Y desde cero, sin tocar nada mas, ya organiza fotos/videos/musica/comprimidos/
instaladores/documentos por tipo. Los Temas personalizados (banco, gimnasio,
apps...) se anaden despues desde la propia interfaz si quieren.

## Anadir/quitar categorias base

Los Temas (banco, gimnasio, apps...) se gestionan desde la interfaz, en
Ajustes — no hace falta tocar ningun fichero para eso. Solo para cambiar las
categorias base (fotos, videos, documentos...) hay que editar
`backend/config/categories.json`: que extensiones caen en cada una y en que
carpeta se guardan. No hace falta reiniciar la base de datos para este
cambio, solo reiniciar el servicio (o `main.py` si lo tienes abierto a mano).
