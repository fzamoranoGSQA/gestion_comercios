from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
import base64
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from cryptography.fernet import Fernet


class Comercio(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    history = HistoricalRecords()  # 👈 agrega la auditoría automática
    uen = models.CharField(max_length=100, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo'),
            ('Suspendido', 'Suspendido')
        ],
    )
    tipo = models.CharField(max_length=50, blank=True)
    pais = models.CharField(max_length=50, blank=True)
    periodo_centinela = models.CharField(max_length=50, blank=True)
    hora_centinela = models.CharField(max_length=50, blank=True)
    periodo_ejecucion = models.CharField(max_length=50, blank=True)
    hora_ejecucion = models.CharField(max_length=300, null=True, blank=True)
    hora_reintentos = models.CharField(max_length=300, null=True, blank=True)
    nombre_servidor = models.CharField(max_length=100, blank=True)
    ubicacion_servidor = models.CharField(max_length=100, blank=True)
    nombre_contacto = models.CharField(max_length=100, blank=True)
    email_contacto = models.EmailField(max_length=254, blank=False, null=False)
    transformaciones = models.CharField(
        max_length=10,
        choices=[
            ('Si', 'Sí'),
            ('No', 'No')
        ]
    )
    fecha_inicio_soporte = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=200)
    history = HistoricalRecords()  # 👈 agrega la auditoría automática
    comercios = models.ManyToManyField(
        'Comercio',
         through='ProveedorComercio',
         related_name='proveedores'
    )
    ean = models.CharField(max_length=50, unique=True)
    periodo_ejecucion = models.CharField(max_length=50, null=True, blank=True)
    hora_ejecucion = models.CharField(max_length=300, null=True, blank=True)
    hora_reintentos = models.CharField(max_length=300, null=True, blank=True)
    cantidad_conexiones = models.PositiveIntegerField(default=0)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo'),
            ('Suspendido', 'Suspendido'),
        ]
    )
    documentos_descarga = models.CharField(
        max_length=200,
        choices=[
            ('Ventas e Inventarios', 'Ventas e Inventarios'),
            ('Ordenes de Compra', 'Ordenes de Compra'),
            ('Ventas Inventarios/Ordenes de Compra', 'Ventas Inventarios/Ordenes de Compra'),
        ]
    )
    tipo_ejecucion = models.CharField(
        max_length=15,
        choices=[
            ('Serie', 'Serie'),
            ('Paralelo', 'Paralelo')
        ]
    )
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_proveedor

# --- Función global para obtener el cifrador ---
def get_fernet():
    key = getattr(settings, "FERNET_KEY", None)
    if not key:
        raise ImproperlyConfigured("No se encontró la clave FERNET en settings.py")
    # Asegurar que la clave esté en formato bytes
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

class ProveedorComercio(models.Model):
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name="proveedor_comercios"
    )
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.CASCADE
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ("Activo", "Activo"),
            ("Inactivo", "Inactivo"),
            ("Suspendido", "Suspendido"),
        ]
    )
    class Meta:
        unique_together = ("proveedor", "comercio")

    def __str__(self):
        return f"{self.proveedor} - {self.comercio} ({self.estado})"



class RutaEntrega(models.Model):
    ESTADOS = [
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    ]

    nombre_servidor_sftp = models.CharField(max_length=100)
    history = HistoricalRecords()
    user_sftp = models.CharField(max_length=100)
    _password_sftp = models.BinaryField(db_column='password_sftp', null=True, blank=True)  # campo real cifrado
    
    @property
    def password_sftp(self):
        """Descifra la contraseña antes de devolverla."""
        if not self._password_sftp:
            return None
        try:
            f = get_fernet()
            return f.decrypt(self._password_sftp).decode()
        except Exception:
            return "••••••••"  # en caso de error, muestra marcador oculto

    @password_sftp.setter
    def password_sftp(self, value):
        """Cifra el password antes de guardar."""
        if value:
            f = get_fernet()
            self._password_sftp = f.encrypt(value.encode())  # ✅ sin .decode()
        else:
            self._password_sftp = None

    puerto_sftp = models.PositiveIntegerField(default=22)
    ruta_sftp_produccion = models.CharField(max_length=255, blank=True, null=True)
    ruta_sftp_pruebas = models.CharField(max_length=255, blank=True, null=True)
    estado_sftp = models.CharField(max_length=10, choices=ESTADOS, blank=True, null=True)

    # Relaciones
    comercios = models.ManyToManyField("Comercio", related_name="rutas_entrega")
    proveedores = models.ManyToManyField("Proveedor", related_name="rutas_entrega")

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_servidor_sftp} ({self.estado_sftp})"
    
# --- Modelo Servidor ---
class Servidor(models.Model):
    ESTADOS = [
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    ]

    nombre_servidor_rpa = models.CharField(max_length=100)
    history = HistoricalRecords()
    ip_servidor_rpa = models.CharField(max_length=100)
    user_rpa = models.CharField(max_length=100)

    # 🔒 Campo cifrado (binario, no texto plano)
    _password_rpa = models.BinaryField(db_column="password_rpa", blank=True, null=True)

    @property
    def password_rpa(self):
        """Descifra la contraseña RPA solo si existe."""
        if not self._password_rpa:
            return None
        try:
            f = get_fernet()
            return f.decrypt(self._password_rpa).decode()
        except Exception as e:
            print("❌ Error al descifrar password_rpa:", e)
            return "••••••••"

    @password_rpa.setter
    def password_rpa(self, value):
        """Cifra la contraseña RPA antes de guardarla."""
        if value:
            f = get_fernet()
            self._password_rpa = f.encrypt(value.encode())
        else:
            self._password_rpa = None

    cantidad_rpa = models.PositiveIntegerField(default=0)
    puerto_rpa = models.CharField(max_length=100)
    pais_rpa = models.CharField(max_length=100)
    estado_rpa = models.CharField(max_length=10, choices=ESTADOS, blank=True, null=True)

    # Relaciones
    comercios = models.ManyToManyField("Comercio", related_name="servidores")

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_servidor_rpa} ({self.estado_rpa})"