03_Vistas_y_Flujos.md
# 🖥️ Vistas y Flujos de Negocio

## 1. vistas.py
| Vista | Tipo | Descripción |
|--------|------|-------------|
| `proveedores(request)` | Función | Listar y buscar proveedores activos. |
| `rutas(request)` | Función | Muestra comercios activos y proveedores asociados. |
| `datos_servidor(request)` | Función | Lista servidores con conteo de proveedores activos. |

## 2. Flujos principales

### 🔹 Flujo: Registro de Proveedor
1. Usuario ingresa datos en formulario.
2. Django valida EAN único.
3. Guarda el proveedor.
4. Registra evento en auditoría.
5. Muestra mensaje de éxito.

### 🔹 Flujo: Conteo de Proveedores Activos por Servidor
1. Se obtiene `Servidor` y sus `comercios`.
2. Se filtran `Proveedor` activos asociados a esos comercios.
3. Se muestra conteo en la lista.