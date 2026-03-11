from rest_framework import serializers
from .models import Comercio, Servidor, Proveedor, RutaEntrega, ProveedorComercio


# --- COMERCIO ---
class ComercioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comercio
        fields = '__all__'


# --- SERVIDOR ---
class ServidorSerializer(serializers.ModelSerializer):
    comercios = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Comercio.objects.all()
    )

    class Meta:
        model = Servidor
        fields = '__all__'


# --- SERIALIZER INTERMEDIO (PRIMERO) ---
class ProveedorComercioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProveedorComercio
        fields = ['comercio', 'estado']


# --- PROVEEDOR ---
class ProveedorSerializer(serializers.ModelSerializer):
    comercios = ProveedorComercioSerializer(
        source='proveedorcomercio_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Proveedor
        fields = '__all__'



# --- RUTA ENTREGA ---
class RutaEntregaSerializer(serializers.ModelSerializer):
    comercios = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Comercio.objects.all()
    )
    proveedores = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Proveedor.objects.all()
    )

    password_sftp = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = RutaEntrega
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password_sftp', None)
        comercios = validated_data.pop('comercios', [])
        proveedores = validated_data.pop('proveedores', [])

        instance = RutaEntrega(**validated_data)

        if password:
            instance.password_sftp = password

        instance.save()
        instance.comercios.set(comercios)
        instance.proveedores.set(proveedores)

        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password_sftp', None)
        comercios = validated_data.pop('comercios', None)
        proveedores = validated_data.pop('proveedores', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.password_sftp = password

        instance.save()

        if comercios is not None:
            instance.comercios.set(comercios)

        if proveedores is not None:
            instance.proveedores.set(proveedores)

        return instance