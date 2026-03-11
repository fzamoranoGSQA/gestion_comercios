from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from core import views
from django.conf import settings
from django.conf.urls.static import static
import os
from core.views import limpiar_proveedores
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import ComercioViewSet, ServidorViewSet, ProveedorViewSet, RutaEntregaViewSet
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)


router = DefaultRouter()
router.register(r'comercios', ComercioViewSet)
router.register(r'servidores', ServidorViewSet)
router.register(r'proveedores', ProveedorViewSet)
router.register(r'rutaentrega', RutaEntregaViewSet)

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    #Token API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

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
    
    #Exportar Comerios Excel
        
    path("exportar-comercios/", views.exportar_comercios_excel, name="exportar_comercios"), 
    
    #Exportar Proveedores Excel   
    
    path("exportar-proveedores/", views.exportar_proveedores_excel, name="exportar_proveedores"),

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




