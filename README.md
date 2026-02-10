# 🧩 Gestión de Comercios — Plataforma de Administración RPA Web

Sistema desarrollado en **Django** para la gestión integral de **Comercios**, **Proveedores**, **Servidores** y **Rutas de Entrega**.  
Permite administrar relaciones comerciales, automatizar procesos y mantener trazabilidad mediante auditoría integrada.

---

## 📂 Estructura General del Proyecto

gestion_comercios/
├── core/ # Aplicación principal
│ ├── models.py # Modelos de datos
│ ├── views.py # Lógica de vistas
│ ├── admin.py # Configuración del panel administrativo
│ ├── templates/ # Interfaces HTML
│ ├── static/ # Recursos estáticos (CSS, JS, imágenes)
│ └── docs/ # Documentación técnica y funcional
│ ├── 00_ResumenGeneral.md
│ ├── 01_ArquitecturaTecnica.md
│ ├── 02_Modelos.md
│ ├── 03_Vistas_y_Flujos.md
│ ├── 04_Templates_y_UI.md
│ ├── 05_API_Endpoints.md
│ ├── 06_Seguridad_y_Autenticacion.md
│ ├── 07_Guia_Instalacion_y_Despliegue.md
│ └── 08_Casos_Uso_Funcionales.md
├── manage.py
└── README.md

yaml
Copiar código

---

## 🧠 Resumen Ejecutivo

La aplicación **Gestión de Comercios** soporta los procesos de administración de relaciones entre **comercios**, **proveedores** y **servidores**, incluyendo la gestión de rutas de entrega y la trazabilidad de acciones mediante auditoría histórica.

Funcionalidades principales:
- Gestión de **Comercios** y **Proveedores activos**.
- Relación muchos-a-muchos entre **Comercio ↔ Proveedor**.
- Registro de **Servidores** asociados a comercios.
- Control de **Rutas de entrega** con estado y configuración.
- Auditoría completa de cambios (`django-simple-history`).
- Autenticación segura con `LoginRequiredMixin` y permisos de usuario.
- Interfaz moderna con Bootstrap y componentes reutilizables.

---

## 🧩 Documentación Detallada

| Sección | Descripción | Enlace |
|----------|--------------|--------|
| 📄 **00_ResumenGeneral** | Introducción y objetivos del sistema | [Ver documento](core/docs/00_ResumenGeneral.md) |
| 🏗️ **01_Arquitectura Técnica** | Estructura de capas, dependencias, módulos y patrones de diseño | [Ver documento](core/docs/01_ArquitecturaTecnica.md) |
| 🗃️ **02_Modelos** | Modelos Django, campos, relaciones y diagrama ER | [Ver documento](core/docs/02_Modelos.md) |
| 🔁 **03_Vistas y Flujos** | Lógica de negocio, vistas y flujos de interacción | [Ver documento](core/docs/03_Vistas_y_Flujos.md) |
| 🎨 **04_Templates y UI** | Detalles de la interfaz y plantillas HTML | [Ver documento](core/docs/04_Templates_y_UI.md) |
| 🔌 **05_API Endpoints** | Endpoints internos y externos disponibles | [Ver documento](core/docs/05_API_Endpoints.md) |
| 🔐 **06_Seguridad y Autenticación** | Mecanismos de autenticación, permisos y protección de rutas | [Ver documento](core/docs/06_Seguridad_y_Autenticacion.md) |
| ⚙️ **07_Guía de Instalación y Despliegue** | Instalación local, despliegue y dependencias | [Ver documento](core/docs/07_Guia_Instalacion_y_Despliegue.md) |
| 🧾 **08_Casos de Uso Funcionales** | Escenarios de uso representativos del sistema | [Ver documento](core/docs/08_Casos_Uso_Funcionales.md) |

---

## 🧱 Diagrama de Modelos

> Generado automáticamente con `django-extensions` y `pydot`.

```bash
python manage.py graph_models core -o core/docs/diagrama_modelos.png