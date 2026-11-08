#!/usr/bin/env python3
"""
/**
 * Verificación previa al despliegue de la landing de El Regalo.
 * La ejecuta GitHub Actions en cada push (y se puede correr en local con
 * `python3 scripts/verificar.py`). Si algo falla, el despliegue se detiene y la
 * versión publicada sigue siendo la anterior, así nunca se publica una página rota.
 *
 * Revisa:
 *  1. Que exista index.html con <title> y meta description.
 *  2. Que cada archivo local referenciado (src, href, srcset, data-full y las
 *     fotos de HABITACIONES) exista en el repositorio.
 *  3. Que el JavaScript del <script> no tenga errores de sintaxis (con Node).
 *  4. Que ninguna imagen pese más de 600 KB (avisa; no detiene el despliegue).
 **/
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
INDEX = RAIZ / "index.html"
LIMITE_KB = 600

errores, avisos = [], []

# 1. El archivo principal y su SEO básico.
if not INDEX.exists():
    sys.exit("ERROR: no existe index.html")
html = INDEX.read_text(encoding="utf-8")
# Los comentarios HTML mencionan "<script>" y rutas de ejemplo: se quitan antes de analizar.
html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
if not re.search(r"<title>[^<]+</title>", html):
    errores.append("Falta <title> en index.html")
if 'name="description"' not in html:
    errores.append("Falta <meta name=\"description\"> en index.html")

# 2. Rutas locales: atributos HTML y rutas 'img/...' dentro del script (HABITACIONES).
rutas = set()
for attr, valor in re.findall(r'\b(src|href|data-full)="([^"]+)"', html):
    rutas.add(valor)
for srcset in re.findall(r'srcset="([^"]+)"', html):
    rutas.update(parte.strip().split()[0] for parte in srcset.split(","))
rutas.update(re.findall(r"'(img/[^']+)'", html))
for ruta in sorted(rutas):
    # Se ignoran enlaces externos, anclas, teléfonos y plantillas de JS.
    if re.match(r"^(https?:|mailto:|tel:|#|data:|\$\{)", ruta) or "${" in ruta:
        continue
    archivo = RAIZ / ruta.split("?")[0].split("#")[0]
    if not archivo.exists():
        errores.append(f"Archivo no encontrado: {ruta}")

# 3. Sintaxis del JavaScript (Node está disponible en GitHub Actions).
scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
if shutil.which("node"):
    for i, codigo in enumerate(scripts, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(codigo)
        res = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
        if res.returncode != 0:
            errores.append(f"Error de sintaxis en el <script> {i}:\n{res.stderr.strip()}")
else:
    avisos.append("Node no está instalado: se omitió la revisión del JavaScript")

# 4. Peso de las imágenes.
for img in (RAIZ / "img").rglob("*"):
    if img.is_file() and img.stat().st_size > LIMITE_KB * 1024:
        avisos.append(f"Imagen pesada ({img.stat().st_size // 1024} KB): {img.relative_to(RAIZ)}")

# Resultado.
for a in avisos:
    print(f"AVISO: {a}")
if errores:
    for e in errores:
        print(f"ERROR: {e}")
    sys.exit(f"\n{len(errores)} error(es): no se despliega.")
print(f"OK: {len(rutas)} rutas revisadas, {len(scripts)} script(s) válidos. Listo para desplegar.")
