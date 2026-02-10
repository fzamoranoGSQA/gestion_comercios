4. Descripción técnica

Modelos principales: Comercio, Proveedor, Servidor, RutaEntrega

Relaciones clave:

Proveedor ↔ Comercio → ManyToMany

Servidor ↔ Comercio → ManyToMany

Auditoría: SimpleHistory activa en todos los modelos críticos.


---

### 🧩 **02_Modelos.md**
```markdown
# 🧩 Modelos de Datos

## Modelo: Comercio
| Campo | Tipo | Descripción |
|--------|------|-------------|
| nombre | CharField(200) | Nombre del comercio |
| estado | CharField | Activo / Inactivo |

## Modelo: Proveedor
| Campo | Tipo | Descripción |
|--------|------|-------------|
| nombre_proveedor | CharField(200) | Nombre del proveedor |
| ean | CharField(50) | Código único EAN |
| estado | CharField | Activo / Inactivo |
| comercios | ManyToMany(Comercio) | Comercios asociados |

## Modelo: Servidor
| Campo | Tipo | Descripción |
|--------|------|-------------|
| nombre_servidor_rpa | CharField(200) | Identificador del servidor |
| comercios | ManyToMany(Comercio) | Comercios asociados al servidor |

## Modelo: RutaEntrega
| Campo | Tipo | Descripción |
|--------|------|-------------|
| nombre_servidor_sftp | CharField(200) | Servidor SFTP asociado |
| estado_sftp | CharField | Estado de conexión |

## Auditoría (SimpleHistory)
Cada modelo auditable guarda:
- Fecha y usuario del cambio.
- Tipo de operación (creación, actualización, eliminación).
- Valores anteriores y nuevos.