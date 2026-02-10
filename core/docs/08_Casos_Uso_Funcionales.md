📋 **08_Casos_Uso_Funcionales.md**
```markdown
# 📋 Casos de Uso Funcionales

| ID | Descripción | Entradas | Salidas | Regla de negocio | Estado |
|----|--------------|----------|----------|------------------|--------|
| RF-001 | Registrar nuevo proveedor | Nombre, EAN, Estado, Comercios | Mensaje de éxito | EAN debe ser único | ✅ Implementado |
| RF-002 | Asociar proveedor a comercio | ID proveedor, ID comercio | Asociación creada | Solo comercios activos | ✅ Implementado |
| RF-003 | Contar proveedores activos por servidor | ID servidor | Número total | Solo proveedores activos asociados a comercios del servidor | ✅ Implementado |
| RF-004 | Registrar ruta de entrega | Servidor, ruta, estado | Mensaje de confirmación | Servidor debe existir | ✅ Implementado |