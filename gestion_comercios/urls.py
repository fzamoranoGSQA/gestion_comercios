from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from core import views
from django.conf import settings
from django.conf.urls.static import static
import os
from core.views import limpiar_proveedores




urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Proveedores
    path('proveedores/', views.proveedores, name='proveedores'),
    
    # CRUD Proveedores
    path('proveedores/eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),


    # CRUD Comercios
    path('eliminar_comercio/<int:id>/', views.eliminar_comercio, name='eliminar_comercio'),
    path('consultar_comercios/', views.consultar_comercios, name='consultar_comercios'),
    path('proveedores/filtrar/', views.filtrar_proveedores_por_comercio, name='filtrar_proveedores_por_comercio'),
    
    # Acerca de
    path('acercade/', views.acercade, name='acercade'),
    
    
    
    # Datos Servidor
    path('datos_servidor/', views.datos_servidor, name='datos_servidor'),
    path("eliminar_servidor/<int:id>/", views.eliminar_servidor, name="eliminar_servidor"),
    
    # Data Source
    path('data_source/', views.data_source, name='data_source'),
    
    # Rutas
    path("rutas/", views.rutas, name="rutas"),
    path("eliminar_rutas/<int:id>/", views.eliminar_rutas, name="eliminar_rutas"),
        

    # 🔑 Recuperación de contraseña
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset.html',
            email_template_name='registration/password_reset_email.txt',
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done')
        ),
        name='password_reset'
    ),

    path(
        'password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path('limpiar-proveedores/', limpiar_proveedores, name='limpiar_proveedores'),
]
# Servir archivos estáticos y media en desarrollo

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, "core/static"))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




