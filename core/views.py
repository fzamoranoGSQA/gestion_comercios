from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Comercio, Proveedor, RutaEntrega, Servidor
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db.models import Prefetch
from django.db import IntegrityError
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
from core.models import Proveedor, ProveedorComercio, Comercio
from django.db import transaction
from core.models import ProveedorComercio
from .models import Comercio, Servidor, Proveedor, RutaEntrega
from rest_framework import viewsets   
from .serializers import ComercioSerializer, ServidorSerializer, ProveedorSerializer, RutaEntregaSerializer                                                                                                                                                          
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
import openpyxl
from django.http import HttpResponse




# ---------- LOGIN ----------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'login.html')


# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    return redirect('login')


# ---------- DASHBOARD (Consulta / Búsqueda / Creación Rápida) ----------
@login_required(login_url='/')  # redirige al login si no está autenticado
def dashboard(request):
    # ================= CONTEXTO BASE =================
    comercios = Comercio.objects.all()
    proveedores = None
    comercio_seleccionado = None

    # ================= FILTRO POR IDS =================
    comercios_ids = request.GET.get("comercios")
    if comercios_ids:
        ids = [int(i) for i in comercios_ids.split(",") if i.isdigit()]
        comercios = comercios.filter(id__in=ids)

    # ================= PROVEEDORES POR COMERCIO =================
    comercio_id = request.GET.get("comercio_id")
    if comercio_id:
        comercio_seleccionado = get_object_or_404(Comercio, id=comercio_id)
        proveedores = Proveedor.objects.filter(
            comercios__id=comercio_id,
            estado__iexact="Activo"
        )

    # ================= POST =================
    if request.method == "POST":
        accion = request.POST.get("accion")

        # ==========================================
        # 💾 GUARDAR / EDITAR COMERCIO
        # ==========================================
        if accion == "guardar":
            comercio_id = request.POST.get("comercio_id")

            nombre = request.POST.get("nombre", "").strip()
            uen = request.POST.get("uen", "").strip()
            estado = request.POST.get("estado", "").strip()
            tipo = request.POST.get("tipo", "").strip()
            pais = request.POST.get("pais", "").strip()
            transformaciones = request.POST.get("transformaciones", "").strip()
            periodo_centinela = request.POST.get("periodo_centinela", "").strip()
            hora_centinela = request.POST.get("hora_centinela", "").strip()
            periodo_ejecucion = request.POST.get("periodo_ejecucion", "").strip()
            hora_ejecucion = request.POST.get("hora_ejecucion", "").strip()
            hora_reintentos = request.POST.get("hora_reintentos", "").strip()
            nombre_servidor = request.POST.get("nombre_servidor", "").strip()
            ubicacion_servidor = request.POST.get("ubicacion_servidor", "").strip()
            fecha_inicio_soporte = request.POST.get("fecha_inicio_soporte", "").strip()
            observaciones = request.POST.get("observaciones", "").strip()
            comercios_ids = request.POST.getlist("comercios")
            estados_por_comercio = {
                k.replace("estado_comercio[", "").replace("]", ""): v
                for k, v in request.POST.items()
                if k.startswith("estado_comercio[")
            }


            # ---------- VALIDACIÓN BÁSICA ----------
            if not nombre or not uen or not estado:
                messages.error(
                    request,
                    "⚠️ Nombre, UEN y Estado son obligatorios."
                )
                return redirect("dashboard")

            # ---------- EDITAR ----------
            if comercio_id:
                comercio = get_object_or_404(Comercio, id=comercio_id)

                if Comercio.objects.filter(
                    nombre__iexact=nombre
                ).exclude(id=comercio_id).exists():
                    messages.error(
                        request,
                        f"⚠️ Ya existe un comercio con el nombre '{nombre}'."
                    )
                    return redirect("dashboard")

            # ---------- CREAR ----------
            else:
                if Comercio.objects.filter(nombre__iexact=nombre).exists():
                    messages.error(
                        request,
                        f"⚠️ Ya existe un comercio con el nombre '{nombre}'."
                    )
                    return redirect("dashboard")

                comercio = Comercio()

            # ---------- ASIGNACIÓN DE CAMPOS ----------
            comercio.nombre = nombre
            comercio.uen = uen
            comercio.estado = estado
            comercio.tipo = tipo
            comercio.pais = pais
            comercio.transformaciones = transformaciones
            comercio.periodo_centinela = periodo_centinela
            comercio.hora_centinela = hora_centinela
            comercio.periodo_ejecucion = periodo_ejecucion
            comercio.hora_ejecucion = hora_ejecucion
            comercio.hora_reintentos = hora_reintentos
            comercio.nombre_servidor = nombre_servidor
            comercio.ubicacion_servidor = ubicacion_servidor
            comercio.observaciones = observaciones
            if fecha_inicio_soporte:
                comercio.fecha_inicio_soporte = datetime.strptime(
                    fecha_inicio_soporte, "%Y-%m-%d"
                ).date()
            else:
                comercio.fecha_inicio_soporte = None
            comercio.save()

            messages.success(
                request,
                f"✅ Comercio '{comercio.nombre}' guardado correctamente."
            )

            return redirect("dashboard")

        # ==========================================
        # 🔍 BUSCAR COMERCIOS
        # ==========================================
        elif accion == "buscar":

            filtros = Q()

            campos_busqueda = [
                "nombre", "uen", "estado", "tipo", "pais",
                "periodo_centinela", "hora_centinela",
                "nombre_servidor", "ubicacion_servidor",
                "fecha_inicio_soporte",
            ]

            for campo in campos_busqueda:
                valor = request.POST.get(campo, "").strip()

                if valor:

                    # estado debe buscarse exacto
                    if campo == "estado":
                        filtros &= Q(**{f"{campo}__iexact": valor})

                    else:
                        filtros &= Q(**{f"{campo}__icontains": valor})

            if filtros:

                comercios = comercios.filter(filtros)

                messages.info(
                    request,
                    f"🔍 Se encontraron {comercios.count()} comercios."
                )

            else:

                messages.warning(
                    request,
                    "⚠️ No se ingresaron criterios de búsqueda."
                )

    # ================= PAGINACIÓN =================
    TOTAL_GENERAL = Comercio.objects.count()
    TOTAL_FILTRADO = comercios.count()

    paginator = Paginator(comercios.order_by("nombre"), 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ================= CONTEXTO FINAL =================
    context = {
        "comercios": page_obj,
        "proveedores": proveedores,
        "comercio_seleccionado": comercio_seleccionado,
        "total_general": TOTAL_GENERAL,
        "total_filtrado": TOTAL_FILTRADO,
        "page_obj": page_obj,
        "start_index": page_obj.start_index(),
    }

    return render(request, "dashboard.html", context)

from django.shortcuts import render
from .models import Comercio


def consultar_comercios(request):
    query = request.GET.get("q", "").strip()

    comercios = Comercio.objects.all()

    if query:
        comercios = comercios.filter(nombre__icontains=query)

    return render(
        request,
        "consultar_comercios.html",
        {
            "comercios": comercios,
            "query": query
        }
    )

# ================= Exporta Comercios Excel =================    
def exportar_comercios_excel(request):
    comercios = Comercio.objects.all().order_by("nombre")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Comercios"

    # Encabezados
    headers = [
        "Nombre", "UEN", "Estado", "Tipo", "País",
        "Transformaciones", "Periodo Centinela", "Hora Centinela",
        "Periodo Ejecución", "Hora Ejecución", "Hora Reintentos",
        "Nombre Servidor", "Ubicación Servidor",
        "Fecha Inicio Soporte", "Nombre Contacto",
        "Email Contacto", "Observaciones"
    ]

    ws.append(headers)

    # Datos
    for c in comercios:
        ws.append([
            c.nombre,
            c.uen,
            c.estado,
            c.tipo,
            c.pais,
            c.transformaciones,
            c.periodo_centinela,
            c.hora_centinela,
            c.periodo_ejecucion,
            c.hora_ejecucion,
            c.hora_reintentos,
            c.nombre_servidor,
            c.ubicacion_servidor,
            str(c.fecha_inicio_soporte),
            c.nombre_contacto,
            c.email_contacto,
            c.observaciones
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = "attachment; filename=comercios.xlsx"

    wb.save(response)

    return response

# ---------- Proveedores (Consulta / Búsqueda / Creación Rápida) ----------
@login_required(login_url='/')
def proveedores(request):

    # ==============================================
    # 🔹 INICIALIZACIÓN (SIEMPRE DEFINIDAS)
    # ==============================================
    proveedor_editando = None
    proveedor_comercios_ids = []

    comercios = Comercio.objects.filter(
        estado__iexact="Activo"
    ).order_by("nombre")

    proveedores_qs = Proveedor.objects.prefetch_related(
        "proveedor_comercios",
        "proveedor_comercios__comercio"
    )

    # ==============================================
    # 🔹 FILTRO POR COMERCIO
    # ==============================================
    comercio_id = request.GET.get("comercio_id")
    if comercio_id:
        proveedores_qs = proveedores_qs.filter(
            comercios__id=comercio_id
        ).distinct()

    # =====================================================
    # ✏️ CARGAR PROVEEDOR PARA EDICIÓN
    # =====================================================
    proveedor_id = request.GET.get("proveedor_id")
    if proveedor_id:
        proveedor_editando = get_object_or_404(Proveedor, id=proveedor_id)
        proveedor_comercios_ids = list(
            proveedor_editando.comercios.values_list("id", flat=True)
        )

    # ==============================================
    # 🔹 POST
    # ==============================================
    if request.method == "POST":
        accion = request.POST.get("accion")

        # =====================================================
        # 💾 GUARDAR / EDITAR PROVEEDOR
        # =====================================================
        if accion == "guardar":
            proveedor_id = request.POST.get("proveedor_id")

            # ---------- CAMPOS OBLIGATORIOS ----------
            nombre = request.POST.get("nombre_proveedor", "").strip()
            ean = request.POST.get("ean", "").strip()
            cantidad_conexiones = request.POST.get("cantidad_conexiones", "").strip()
            documentos_descarga = request.POST.get("documentos_descarga", "").strip()
            comercios_ids = request.POST.getlist("comercios")

            # ---------- CAMPOS OPCIONALES ----------
            periodo_ejecucion = request.POST.get("periodo_ejecucion") or None
            hora_ejecucion = request.POST.get("hora_ejecucion") or None
            hora_reintentos = request.POST.get("hora_reintentos") or None
            tipo_ejecucion = request.POST.get("tipo_ejecucion") or None
            observaciones = request.POST.get("observaciones", "").strip()

            # ---------- VALIDACIÓN OBLIGATORIA ----------
            if not all([
                nombre,
                ean,
                cantidad_conexiones,
                documentos_descarga,
                comercios_ids
            ]):
                messages.error(
                    request,
                    "⚠️ Nombre, EAN, Cantidad de Conexiones, Documentos Descarga y Comercios son obligatorios."
                )
                return redirect("proveedores")

            # ---------- EDITAR ----------
            if proveedor_id:
                proveedor = get_object_or_404(Proveedor, id=proveedor_id)

                if Proveedor.objects.filter(ean=ean).exclude(id=proveedor_id).exists():
                    messages.error(
                        request,
                        f"⚠️ Ya existe un proveedor con el EAN {ean}."
                    )
                    return redirect("proveedores")

            # ---------- CREAR ----------
            else:
                if Proveedor.objects.filter(ean=ean).exists():
                    messages.error(
                        request,
                        f"⚠️ Ya existe un proveedor con el EAN {ean}."
                    )
                    return redirect("proveedores")

                proveedor = Proveedor()

            # ---------- ASIGNACIÓN ----------
            proveedor.nombre_proveedor = nombre
            proveedor.ean = ean
            proveedor.cantidad_conexiones = int(cantidad_conexiones)
            proveedor.documentos_descarga = documentos_descarga
            proveedor.periodo_ejecucion = periodo_ejecucion
            proveedor.hora_ejecucion = hora_ejecucion
            proveedor.hora_reintentos = hora_reintentos
            proveedor.tipo_ejecucion = tipo_ejecucion
            proveedor.observaciones = observaciones

            proveedor.save()

            # ---------- RELACIÓN M2M ----------
            with transaction.atomic():
                ProveedorComercio.objects.filter(proveedor=proveedor).delete()

                relaciones = []
                for comercio_id in comercios_ids:
                    estado_comercio = request.POST.get(f"estado_comercio[{comercio_id}]")

                    if not estado_comercio:
                        messages.error(
                            request,
                            "⚠️ Todos los comercios deben tener un estado asignado."
                        )
                        return redirect("proveedores")

                    relaciones.append(
                        ProveedorComercio(
                            proveedor=proveedor,
                            comercio_id=comercio_id,
                            estado=estado_comercio
                        )
                    )

                ProveedorComercio.objects.bulk_create(relaciones)

            messages.success(
                request,
                f"✅ Proveedor '{proveedor.nombre_proveedor}' guardado correctamente."
            )
            return redirect("proveedores")

        # =====================================================
        # 🔍 BUSCAR PROVEEDORES
        # =====================================================
        elif accion == "buscar":
            filtros = Q()

            nombre = request.POST.get("nombre_proveedor", "").strip()
            ean = request.POST.get("ean", "").strip()
            documentos_descarga = request.POST.get("documentos_descarga", "").strip()
            comercios_ids = request.POST.getlist("comercios")
            

            if not any([nombre, ean, documentos_descarga, comercios_ids]):
                messages.warning(
                    request,
                    "⚠️ Debe ingresar al menos un criterio de búsqueda."
                )
                return redirect("proveedores")

            if nombre:
                filtros &= Q(nombre_proveedor__icontains=nombre)
            if ean:
                filtros &= Q(ean__icontains=ean)
            if documentos_descarga:
                filtros &= Q(documentos_descarga__icontains=documentos_descarga)
            if comercios_ids:
                filtros &= Q(comercios__id__in=comercios_ids)

            proveedores_qs = proveedores_qs.filter(filtros).distinct()
            
    # ==============================================
    # 🔢 MÉTRICAS
    # ==============================================
    TOTAL_GENERAL = Proveedor.objects.count()
    TOTAL_FILTRADO = proveedores_qs.count()

    total_conexiones = proveedores_qs.aggregate(
        total=Sum("cantidad_conexiones")
    )["total"] or 0

    # ==============================================
    # 📄 PAGINACIÓN
    # ==============================================
    paginator = Paginator(
        proveedores_qs.order_by("nombre_proveedor"), 15
    )
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    start_index = page_obj.start_index() if TOTAL_FILTRADO else 0
    
    
    proveedores_data = [
    {
        "id": p.id,
        "comercios_ids": list(p.comercios.values_list("id", flat=True)),
        "estados": {
            pc.comercio.id: pc.estado
            for pc in p.proveedor_comercios.all()
        }
    }
    for p in proveedores_qs
]

    # ==============================================
    # 🔚 CONTEXTO FINAL
    # ==============================================
    context = {
        "proveedores": page_obj,
        "comercios": comercios,
        "proveedor_editar": proveedor_editando,
        "proveedor_comercios_ids": proveedor_comercios_ids,
        "total_general": TOTAL_GENERAL,
        "total_filtrado": TOTAL_FILTRADO,
        "total_conexiones": total_conexiones,
        "page_obj": page_obj,
        "start_index": start_index,
        
    }

    return render(request, "proveedores.html", context)

# Exporta Proveedores a Excel
    
def exportar_proveedores_excel(request):

        proveedores = Proveedor.objects.prefetch_related(
            "comercios",
            "proveedor_comercios__comercio"
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Proveedores"

        headers = [
            "Nombre",
            "EAN",
            "Estado Comercio",
            "Documentos Descarga",
            "Periodo Ejecucion",
            "Hora Ejecucion",
            "Hora Reintentos",
            "Tipo Ejecucion",
            "Cantidad Conexiones",
            "Comercios Asociados",
            "Observaciones"
        ]

        ws.append(headers)

        for p in proveedores:

            estados = ", ".join(
                f"{pc.comercio.nombre}-{pc.estado}"
                for pc in p.proveedor_comercios.all()
            )

            comercios = ", ".join(
                c.nombre for c in p.comercios.all()
            )

            ws.append([
                p.nombre_proveedor,
                p.ean,
                estados,
                p.documentos_descarga,
                p.periodo_ejecucion,
                p.hora_ejecucion,
                p.hora_reintentos,
                p.tipo_ejecucion,
                p.cantidad_conexiones,
                comercios,
                p.observaciones
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = "attachment; filename=proveedores.xlsx"

        wb.save(response)

        return response


# -------- FUNCIONES AUXILIARES --------

@login_required(login_url='/')
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    try:
        with transaction.atomic():

            # 🔥 LIMPIAR RELACIÓN M2M (ESTO ES CLAVE)
            proveedor.comercios.clear()

            # 🔥 AHORA SÍ BORRAR EL PROVEEDOR
            proveedor.delete()

        messages.success(
            request,
            f"🗑️ Proveedor '{proveedor.nombre_proveedor}' eliminado correctamente."
        )

    except Exception as e:
        messages.error(
            request,
            f"❌ Error al eliminar el proveedor: {e}"
        )

    return redirect("proveedores")





def eliminar_comercio(request, id):
    comercio = get_object_or_404(Comercio, pk=id)
    nombre = comercio.nombre
    comercio.delete()
    messages.success(request, f"🗑️ Comercio '{nombre}' eliminado correctamente.")
    return redirect('dashboard')


def filtrar_proveedores_por_comercio(request):
    comercio_id = request.GET.get('comercio_id')
    comercio = Comercio.objects.filter(id=comercio_id).first()
    proveedores = (
        Proveedor.objects.filter(comercios=comercio, estado='Activo')
        .distinct() if comercio else Proveedor.objects.none()
    )

    return render(request, 'proveedores.html', {
        'proveedores': proveedores,
        'comercio': comercio,
    })
    
    
def acercade(request):
    return render(request, 'acercade.html')

def ruta_entrega(request):
    return render(request, 'ruta_entrega.html')

def datos_servidor(request):
    return render(request, 'datos_servidor.html')

def data_source(request):
    return render(request, 'data_source.html')


# ---------- Rutas (Consulta / Búsqueda / Creación Rápida) ----------
@login_required(login_url='/')  # Redirige al login si no está autenticado
def rutas(request):

    # ================= DATOS BASE =================
    comercios = Comercio.objects.filter(estado__iexact="Activo").order_by("nombre")

    proveedores = (
        Proveedor.objects
        .filter(estado__in=["Activo", "Suspendido", "Inactivo"])
        .order_by("nombre_proveedor")
    )

    rutas_qs = RutaEntrega.objects.all().prefetch_related("comercios", "proveedores").order_by("id")

    # ================= POST =================
    if request.method == "POST":

        accion = request.POST.get("accion")
        ruta_id = request.POST.get("ruta_id")

        # ==========================================
        # GUARDAR / EDITAR
        # ==========================================
        if accion == "guardar":

            nombre_servidor = request.POST.get("nombre_servidor_sftp", "").strip()
            user_sftp = request.POST.get("user_sftp", "").strip()
            password_sftp = request.POST.get("password_sftp", "").strip()
            puerto_sftp = request.POST.get("puerto_sftp", "").strip()
            estado_sftp = request.POST.get("estado_sftp", "Activo").strip()
            ruta_sftp_produccion = request.POST.get("ruta_sftp_produccion", "").strip()
            ruta_sftp_pruebas = request.POST.get("ruta_sftp_pruebas", "").strip()

            # --- Crear o editar ---
            if ruta_id:
                ruta = get_object_or_404(RutaEntrega, id=ruta_id)
                mensaje_accion = "actualizada"
            else:
                ruta = RutaEntrega()
                mensaje_accion = "creada"

            # --- Validación ---
            campos_obligatorios = {
                "nombre_servidor_sftp": nombre_servidor,
                "user_sftp": user_sftp,
                "puerto_sftp": puerto_sftp,
                "estado_sftp": estado_sftp,
                "ruta_sftp_produccion": ruta_sftp_produccion,
                "ruta_sftp_pruebas": ruta_sftp_pruebas,
            }

            if not ruta_id:
                campos_obligatorios["password_sftp"] = password_sftp

            faltantes = [
                campo.replace("_", " ").capitalize()
                for campo, valor in campos_obligatorios.items()
                if not valor
            ]

            if faltantes:
                messages.error(
                    request,
                    f"⚠️ Los siguientes campos son obligatorios: {', '.join(faltantes)}."
                )
                return redirect("rutas")

            # --- Puerto ---
            try:
                puerto_sftp = int(puerto_sftp)
            except:
                messages.warning(
                    request,
                    "⚠️ El puerto SFTP no es válido, se usará 22 por defecto."
                )
                puerto_sftp = 22

            # --- Asignación ---
            ruta.nombre_servidor_sftp = nombre_servidor
            ruta.user_sftp = user_sftp

            if password_sftp and password_sftp != "••••••••":
                ruta.password_sftp = password_sftp

            ruta.puerto_sftp = puerto_sftp
            ruta.estado_sftp = estado_sftp
            ruta.ruta_sftp_produccion = ruta_sftp_produccion
            ruta.ruta_sftp_pruebas = ruta_sftp_pruebas

            ruta.save()

            # --- Relaciones ManyToMany ---
            comercios_ids = request.POST.getlist("comercios") or [request.POST.get("comercio")]
            proveedores_ids = request.POST.getlist("proveedores") or [request.POST.get("proveedor")]

            if comercios_ids:
                ruta.comercios.set([c for c in comercios_ids if c])

            if proveedores_ids:
                ruta.proveedores.set([p for p in proveedores_ids if p])

            messages.success(request, f"✅ Ruta {mensaje_accion} correctamente.")
            return redirect("rutas")

        # ==========================================
        # BUSCAR
        # ==========================================
        elif accion == "buscar":

            filtros = Q()

            nombre_servidor = request.POST.get("nombre_servidor_sftp", "").strip()
            user_sftp = request.POST.get("user_sftp", "").strip()
            puerto_sftp = request.POST.get("puerto_sftp", "").strip()
            estado_sftp = request.POST.get("estado_sftp", "").strip()
            ruta_sftp_produccion = request.POST.get("ruta_sftp_produccion", "").strip()
            ruta_sftp_pruebas = request.POST.get("ruta_sftp_pruebas", "").strip()
            comercio_id = request.POST.get("comercio", "").strip()
            proveedor_id = request.POST.get("proveedor", "").strip()

            if nombre_servidor:
                filtros &= Q(nombre_servidor_sftp__icontains=nombre_servidor)

            if user_sftp:
                filtros &= Q(user_sftp__icontains=user_sftp)

            if puerto_sftp:
                filtros &= Q(puerto_sftp__icontains=puerto_sftp)

            if estado_sftp:
                filtros &= Q(estado_sftp__iexact=estado_sftp)

            if ruta_sftp_produccion:
                filtros &= Q(ruta_sftp_produccion__icontains=ruta_sftp_produccion)

            if ruta_sftp_pruebas:
                filtros &= Q(ruta_sftp_pruebas__icontains=ruta_sftp_pruebas)

            if comercio_id:
                filtros &= Q(comercios__id=comercio_id)

            if proveedor_id:
                filtros &= Q(proveedores__id=proveedor_id)

            if filtros:
                rutas_qs = rutas_qs.filter(filtros).distinct()

                if rutas_qs.exists():
                    messages.success(
                        request,
                        f"🔍 Se encontraron {rutas_qs.count()} rutas que coinciden con los criterios."
                    )
                else:
                    messages.info(
                        request,
                        "🔍 No se encontraron rutas con esos filtros."
                    )
            else:
                messages.warning(
                    request,
                    "⚠️ No se ingresó ningún criterio de búsqueda."
                )

    # ================= PAGINACIÓN =================
    paginator = Paginator(rutas_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    start_index = (page_obj.number - 1) * paginator.per_page + 1

    # ================= SERIALIZACIÓN =================
    rutas_data = []

    for r in rutas_qs:

        rutas_data.append({
            "id": r.id,
            "nombre_servidor_sftp": r.nombre_servidor_sftp,
            "user_sftp": r.user_sftp,
            "password_sftp": "••••••••" if r._password_sftp else "",
            "puerto_sftp": r.puerto_sftp,
            "estado_sftp": r.estado_sftp,
            "ruta_sftp_produccion": r.ruta_sftp_produccion,
            "ruta_sftp_pruebas": r.ruta_sftp_pruebas,
            "comercios_ids": list(r.comercios.values_list("id", flat=True)),
            "proveedores_ids": list(r.proveedores.values_list("id", flat=True)),
        })

    # ================= CONTEXT =================
    context = {

        "comercios": comercios,
        "proveedores": proveedores,

        "rutas": page_obj,
        "page_obj": page_obj,

        "total_rutas": rutas_qs.count(),
        "start_index": start_index,

        "rutas_data": json.dumps(rutas_data, ensure_ascii=False),
    }
    
    print("PROVEEDORES:", list(proveedores.values("id", "nombre_proveedor", "estado")))

    return render(request, "ruta_entrega.html", context)


def eliminar_rutas(request, id):
    ruta = get_object_or_404(RutaEntrega, id=id)
    ruta.delete()
    messages.success(request, f"🗑️ Ruta '{ruta.nombre_servidor_sftp}' eliminada correctamente.")
    return redirect("rutas")

# ---------- Servidores (Creación / Consulta / Edición / Eliminación) ----------
@login_required(login_url='/')  # redirige al login si no está autenticado
def datos_servidor(request):
    comercios = Comercio.objects.filter(estado__iexact="Activo").order_by("nombre")
    servidores_qs = Servidor.objects.prefetch_related("comercios").order_by("nombre_servidor_rpa")

    # --- Serialización para edición y conteo de proveedores ---
    servidores_data = []
    for s in servidores_qs:
        comercios_ids = s.comercios.values_list("id", flat=True)
        cantidad_proveedores = Proveedor.objects.filter(
            comercios__id__in=comercios_ids,
            estado__iexact="Activo"
        ).distinct().count()
        s.cantidad_proveedores = cantidad_proveedores

        servidores_data.append({
            "id": s.id,
            "nombre_servidor_rpa": s.nombre_servidor_rpa,
            "ip_servidor_rpa": s.ip_servidor_rpa,
            "user_rpa": s.user_rpa,
            # 🔒 Muestra "••••••••" si existe, None si no está configurado
            "password_rpa": "••••••••" if s._password_rpa else None,
            "cantidad_rpa": s.cantidad_rpa,
            "pais_rpa": s.pais_rpa,
            "puerto_rpa": s.puerto_rpa,
            "estado_rpa": s.estado_rpa,
            "comercios_ids": list(comercios_ids),
            "cantidad_proveedores": cantidad_proveedores,
        })

    # --- Procesamiento POST (crear, editar, buscar, etc.) ---
    if request.method == "POST":
        accion = request.POST.get("accion")
        servidor_id = request.POST.get("servidor_id")

        try:
            # === GUARDAR / EDITAR ===
            if accion == "guardar":
                nombre_servidor_rpa = request.POST.get("nombre_servidor_rpa", "").strip()
                ip_servidor_rpa = request.POST.get("ip_servidor_rpa", "").strip()
                user_rpa = request.POST.get("user_rpa", "").strip()
                password_rpa = request.POST.get("password_rpa", "").strip()
                puerto_rpa = request.POST.get("puerto_rpa", "").strip()
                pais_rpa = request.POST.get("pais_rpa", "").strip()
                estado_rpa = request.POST.get("estado_rpa", "").strip()
                comercios_ids = request.POST.getlist("comercios")

                # Validación de campos
                campos_obligatorios = {
                    "Nombre Servidor RPA": nombre_servidor_rpa,
                    "IP del Servidor": ip_servidor_rpa,
                    "Usuario RPA": user_rpa,
                    "Puerto RPA": puerto_rpa,
                    "Pais RPA": pais_rpa,
                    "Estado Servidor": estado_rpa,
                }

                faltantes = [campo for campo, valor in campos_obligatorios.items() if not valor]
                if not comercios_ids:
                    faltantes.append("Comercios Asociados")

                if faltantes:
                    messages.error(request, f"⚠️ Los siguientes campos son obligatorios: {', '.join(faltantes)}.")
                    return redirect("datos_servidor")

                # --- Crear o editar ---
                if servidor_id:
                    servidor = get_object_or_404(Servidor, pk=servidor_id)

                    if Servidor.objects.filter(nombre_servidor_rpa__iexact=nombre_servidor_rpa).exclude(id=servidor_id).exists():
                        messages.error(request, f"⚠️ Ya existe un servidor con el nombre '{nombre_servidor_rpa}'.")
                        return redirect("datos_servidor")

                    servidor.nombre_servidor_rpa = nombre_servidor_rpa
                    servidor.ip_servidor_rpa = ip_servidor_rpa
                    servidor.user_rpa = user_rpa
                    servidor.puerto_rpa = puerto_rpa
                    servidor.pais_rpa = pais_rpa
                    servidor.estado_rpa = estado_rpa

                    # 🔐 Solo actualizar contraseña si el usuario escribió una nueva
                    if password_rpa and password_rpa != "••••••••":
                        servidor.password_rpa = password_rpa

                    servidor.save()
                    servidor.comercios.set(comercios_ids)
                    messages.success(request, f"✅ Servidor '{nombre_servidor_rpa}' actualizado correctamente.")

                else:
                    if Servidor.objects.filter(nombre_servidor_rpa__iexact=nombre_servidor_rpa).exists():
                        messages.error(request, f"⚠️ Ya existe un servidor con el nombre '{nombre_servidor_rpa}'.")
                        return redirect("datos_servidor")

                    nuevo = Servidor(
                        nombre_servidor_rpa=nombre_servidor_rpa,
                        ip_servidor_rpa=ip_servidor_rpa,
                        user_rpa=user_rpa,
                        puerto_rpa=puerto_rpa,
                        pais_rpa=pais_rpa,
                        estado_rpa=estado_rpa,
                    )

                    if password_rpa:
                        nuevo.password_rpa = password_rpa

                    nuevo.save()
                    nuevo.comercios.set(comercios_ids)
                    messages.success(request, f"✅ Servidor '{nombre_servidor_rpa}' creado correctamente.")

                return redirect("datos_servidor")

        except Exception as e:
            messages.error(request, f"❌ Error al procesar el servidor: {str(e)}")

    # --- Render final ---
    contexto = {
        "comercios": comercios,
        "servidores": servidores_qs,
        "servidores_data": json.dumps(servidores_data, default=str),
    }
    return render(request, "datos_servidor.html", contexto)



# ---------- Eliminar servidor ----------
def eliminar_servidor(request, id):
    servidor = get_object_or_404(Servidor, id=id)
    nombre = servidor.nombre_servidor_rpa
    servidor.delete()
    messages.success(request, f"🗑️ Servidor '{nombre}' eliminado correctamente.")
    return redirect("datos_servidor")



@login_required(login_url='/')
def limpiar_proveedores(request):
    try:
        with transaction.atomic():
            Proveedor.objects.all().delete()

        messages.success(request, "✅ Todos los proveedores fueron eliminados correctamente.")
    except Exception as e:
        messages.error(request, f"❌ Error eliminando proveedores: {e}")

    return redirect('proveedores')

#Exponer APIs

# --- COMERCIO ---
class ComercioViewSet(viewsets.ModelViewSet):
    queryset = Comercio.objects.all()
    serializer_class = ComercioSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['nombre']  # ajusta según tu modelo
    permission_classes = [IsAuthenticated]


# --- SERVIDOR ---
class ServidorViewSet(viewsets.ModelViewSet):
    queryset = Servidor.objects.prefetch_related("comercios").all()
    serializer_class = ServidorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre_servidor_rpa']  # ajusta si aplica
    permission_classes = [IsAuthenticated]


# --- PROVEEDOR ---
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.prefetch_related("comercios").all()
    serializer_class = ProveedorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado', 'tipo_ejecucion']
    permission_classes = [IsAuthenticated]


# --- RUTA ENTREGA ---
class RutaEntregaViewSet(viewsets.ModelViewSet):
    queryset = RutaEntrega.objects.prefetch_related("comercios", "proveedores").all()
    serializer_class = RutaEntregaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado_sftp']
    permission_classes = [IsAuthenticated]

    # 🔥 endpoint custom: /api/rutas-entrega/{id}/proveedores/
    from rest_framework.decorators import action
    from rest_framework.response import Response

    @action(detail=True, methods=['get'])
    def proveedores(self, request, pk=None):
        ruta = self.get_object()
        proveedores = ruta.proveedores.all()
        serializer = ProveedorSerializer(proveedores, many=True)
        return Response(serializer.data)
    
    