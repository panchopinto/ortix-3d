# ORTIX 3D

Sitio web estático en español del proyecto **ORTIX 3D**, del Liceo Bicentenario de Excelencia Polivalente San Nicolás, presentado en la Feria de las Ciencias. Está pensado para abrirse desde un código QR en un celular.

Es HTML, CSS y JavaScript sin dependencias ni servicios externos. Todas las rutas son relativas, así que funciona desde la subruta de GitHub Pages (`https://USUARIO.github.io/ortix-3d/`).

## Contenido del repositorio

```
index.html          Página única con anclas: El desafío, La órtesis, Cómo se hizo, Avances, Compartir QR
.nojekyll           Evita el procesamiento de Jekyll en GitHub Pages
css/styles.css      Estilos (móvil primero)
js/app.js           Navegación, puntos de la fotografía y bloque «Compartir QR»
js/config.js        URL pública (vacía hasta confirmarla; la completa tools/generar_qr.py)
img/                Fotografía optimizada (WebP + JPEG), imagen para compartir y favicon
qr/                 qr-ortix-3d.png y qr-ortix-3d.svg (se generan al confirmar la URL)
tools/              Generador y verificador del QR
```

El sitio solo contiene texto, fotografías del dispositivo aislado y datos agregados. No se deben subir archivos de trabajo ni documentos internos.

## Ver el sitio en local

Desde esta carpeta:

```powershell
python -m http.server 8080
```

y abrir <http://localhost:8080/>. También funciona abriendo `index.html` directamente.

## Publicar en GitHub Pages

Requiere iniciar sesión en la cuenta personal de GitHub de quien publica. Verifica el usuario antes de crear nada:

```powershell
gh auth status
gh api user --jq .login
```

Con el usuario confirmado (reemplaza `USUARIO_CONFIRMADO`):

```powershell
git init -b main
git add .
git commit -m "Sitio ORTIX 3D"
gh repo create USUARIO_CONFIRMADO/ortix-3d --public --source=. --push
gh api -X POST repos/USUARIO_CONFIRMADO/ortix-3d/pages -f "source[branch]=main" -f "source[path]=/"
```

Equivale a **Settings → Pages → Deploy from a branch → `main` y `/(root)`**. Verifica la URL real en esa pantalla (formato previsto: `https://USUARIO_CONFIRMADO.github.io/ortix-3d/`) y comprueba que abre por HTTPS sin iniciar sesión, con imágenes, estilos y scripts cargando.

## Generar el código QR

Con la URL pública ya activa:

```powershell
python -m pip install -r tools/requirements.txt
python tools/generar_qr.py https://USUARIO_CONFIRMADO.github.io/ortix-3d/
python tools/verificar_qr.py https://USUARIO_CONFIRMADO.github.io/ortix-3d/
```

- `generar_qr.py` crea `qr/qr-ortix-3d.png` (24 px por módulo) y `qr/qr-ortix-3d.svg`, con módulos negros, fondo blanco y margen de 4 módulos, y escribe la URL en `js/config.js` para activar el bloque «Compartir QR».
- `verificar_qr.py` decodifica el PNG y el SVG rasterizado y exige que contengan exactamente la URL y el margen mínimo.

Después, `git add qr js/config.js`, `git commit` y `git push`. Para imprimir, coloca el texto «Escanea para conocer ORTIX 3D» fuera del código y prueba el resultado con la cámara de un celular.

## Notas

- La imagen `og:image` usa una ruta relativa. Algunas plataformas de mensajería solo muestran la vista previa si es absoluta; puedes cambiarla por `https://USUARIO_CONFIRMADO.github.io/ortix-3d/img/ortix-compartir.jpg` tras publicar.
- Este sitio no es una guía de fabricación ni de uso de una órtesis y no reemplaza la evaluación de profesionales de la salud.
