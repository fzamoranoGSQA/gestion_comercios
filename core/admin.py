from django.contrib import admin
from .models import Proveedor, Comercio, Servidor, RutaEntrega
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_proveedor', 'estado', 'ean')
    list_filter = ('estado',)
    search_fields = ('nombre_proveedor', 'ean')
    
class ProveedorComercioInline(admin.TabularInline):
    
    extra = 1
   

@admin.register(Comercio)
class ComercioAdmin(SimpleHistoryAdmin):
    list_display = ('nombre', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre',)

@admin.register(Servidor)
class ServidorAdmin(SimpleHistoryAdmin):
    list_display = ('nombre_servidor_rpa', 'estado_rpa')
    search_fields = ('nombre_servidor_rpa',)

@admin.register(RutaEntrega)
class RutaEntregaAdmin(SimpleHistoryAdmin):
    list_display = ('nombre_servidor_sftp', 'estado_sftp')
    search_fields = ('nombre_servidor_sftp',)        