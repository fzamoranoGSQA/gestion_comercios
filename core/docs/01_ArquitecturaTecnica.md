01_ArquitecturaTecnica.md
# ⚙️ Arquitectura Técnica

## 1. Componentes principales
La aplicación está estructurada bajo el patrón **MVT (Model–View–Template)**.



gestion_comercios/
├── core/
│ ├── models.py
│ ├── views.py
│ ├── admin.py
│ ├── urls.py
│ └── templates/core/
├── static/
├── templates/
│ └── base.html
├── manage.py
└── requirements.txt

## 2. Dependencias principales
Django==5.0.3
django-simple-history
django-extensions
drf-yasg

## 3. Diagrama de entidades
Generar automáticamente:
```bash
python manage.py graph_models core -o core/docs/diagrama_modelos.png

Se genera en la raiz el grafico del modelo

