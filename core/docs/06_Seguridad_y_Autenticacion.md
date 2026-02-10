06_Seguridad_y_Autenticacion.md
# 🔒 Seguridad y Autenticación

## 1. Control de acceso
- Todas las vistas están protegidas con `@login_required`.
- Redirección automática a `/login/` si el usuario no está autenticado.

## 2. Roles
- **Superusuario (admin)**: CRUD completo, acceso a auditoría.
- **Usuario estándar**: Lectura / edición controlada.

## 3. Auditoría
Cada cambio en los modelos registrados guarda:
- Usuario responsable (`request.user`)
- Fecha/hora exacta
- Datos previos y nuevos