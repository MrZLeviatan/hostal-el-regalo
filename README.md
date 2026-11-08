# El Regalo · Hostal & Cafetería

Landing informativa de El Regalo (Vereda Palestina, Salento, Quindío) en 5 idiomas.
Un solo `index.html` (HTML + CSS + JS, sin dependencias) y las fotos en `img/`.

**Página publicada:** <https://mrzleviatan.github.io/hostal-el-regalo/>

## Cómo se actualiza (despliegue continuo)

Cada `git push` a `main` ejecuta el flujo [`.github/workflows/desplegar.yml`](.github/workflows/desplegar.yml):

1. **Verificar** (`scripts/verificar.py`): que existan todos los archivos referenciados,
   el SEO básico y que el JavaScript no tenga errores.
2. **Desplegar**: si la verificación pasa, publica en GitHub Pages en ~1 minuto.
   Si falla, la página publicada sigue intacta y GitHub avisa por correo.

```bash
git add -A && git commit -m "Describe el cambio" && git push
```

Para revisar antes de subir: `python3 scripts/verificar.py` y
`python3 -m http.server 5520` → <http://localhost:5520>.

## Qué se edita y dónde (todo en `index.html`)

| Qué | Dónde |
|---|---|
| WhatsApp, teléfonos, Instagram, Facebook, carta | objeto `CONFIG` del `<script>` |
| Habitaciones (fotos, capacidad, baño, textos por idioma) | lista `HABITACIONES` |
| Textos de la página en cada idioma | diccionario `I18N` |
| Colores | variables en `:root` |
| Fotos | carpeta `img/` (WebP) |

## Dominio propio (más adelante)

En el repositorio: **Settings → Pages → Custom domain**, y en el proveedor del dominio un
registro `CNAME` hacia `mrzleviatan.github.io`. Después cambia las URL de las etiquetas
`canonical` y `og:*` del `<head>`.
