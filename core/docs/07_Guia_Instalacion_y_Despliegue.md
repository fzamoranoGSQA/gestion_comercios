07_Guia_Instalacion_y_Despliegue.md
# 🚀 Guía de Instalación y Despliegue

## 1. Requisitos
- Python 3.11
- pip
- virtualenv

## 2. Instalación local
```bash
git clone <repositorio>
cd gestion_comercios
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

3. Despliegue (Linux o servidor)

Configurar variables de entorno en .env.

Usar gunicorn o uwsgi + nginx.

Asegurar HTTPS.