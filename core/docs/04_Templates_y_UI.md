04_Templates_y_UI.md
# 🎨 Templates y UI

## 1. Base HTML
`templates/base.html`
- Define estructura global.
- Incluye Bootstrap, íconos y favicon.
- Bloques: `{% block title %}`, `{% block content %}`.

## 2. Plantillas principales
| Template | Propósito |
|-----------|------------|
| `proveedores.html` | Listado y búsqueda de proveedores. |
| `rutas.html` | Gestión de rutas de entrega. |
| `datos_servidor.html` | Conteo de proveedores activos por servidor. |

## 3. Estilo
- Basado en Bootstrap 5.
- Íconos: `bi bi-...`
- Clases usadas: `table table-striped`, `alert alert-success`, etc.