from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date, timedelta

from .models import Libro, Autor, Categoria, Editorial, Prestamo
from .serializers import (
    LibroSerializer, AutorSerializer, CategoriaSerializer,
    EditorialSerializer, PrestamoSerializer
)

# ========== VIEWSETS REST API ==========

class LibroViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de libros via API REST"""
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'autor', 'editorial', 'estado']
    search_fields = ['titulo', 'isbn', 'autor__nombre', 'autor__apellido']
    ordering_fields = ['titulo', 'fecha_publicacion', 'stock_disponible']
    ordering = ['titulo']

class AutorViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de autores"""
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'apellido', 'nacionalidad']
    ordering_fields = ['nombre', 'apellido']
    ordering = ['apellido']

class CategoriaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de categorías"""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

class EditorialViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de editoriales"""
    queryset = Editorial.objects.all()
    serializer_class = EditorialSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

class PrestamoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de préstamos"""
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'usuario', 'libro']
    ordering_fields = ['fecha_prestamo', 'fecha_devolucion_esperada']
    ordering = ['-fecha_prestamo']

# ========== VISTAS TRADICIONALES ==========

def index(request):
    """Página de inicio de la app libros"""
    from django.contrib.auth.models import User
    context = {
        'total_libros': Libro.objects.count(),
        'total_autores': Autor.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado='activo').count(),
        'total_usuarios': User.objects.count(),
    }
    return render(request, 'libros/index.html', context)

def catalogo(request):
    """Vista del catálogo de libros con filtros"""
    libros_list = Libro.objects.select_related('autor', 'categoria', 'editorial').all()
    
    # Aplicar filtros
    categoria_id = request.GET.get('categoria')
    autor_id = request.GET.get('autor')
    estado = request.GET.get('estado')
    
    if categoria_id:
        libros_list = libros_list.filter(categoria_id=categoria_id)
    if autor_id:
        libros_list = libros_list.filter(autor_id=autor_id)
    if estado == 'disponible':
        libros_list = libros_list.filter(stock_disponible__gt=0)
    elif estado == 'prestado':
        libros_list = libros_list.filter(stock_disponible=0)
    
    # Paginación
    paginator = Paginator(libros_list, 12)
    page_number = request.GET.get('page')
    libros = paginator.get_page(page_number)
    
    context = {
        'libros': libros,
        'total_libros': Libro.objects.count(),
        'categorias': Categoria.objects.all(),
        'autores': Autor.objects.all(),
    }
    return render(request, 'libros/catalogo.html', context)

def detalle_libro(request, libro_id):
    """Vista de detalle de un libro"""
    libro = get_object_or_404(
        Libro.objects.select_related('autor', 'categoria', 'editorial'),
        id=libro_id
    )
    context = {'libro': libro}
    return render(request, 'libros/detalle_libro.html', context)

def busqueda(request):
    """Vista de búsqueda de libros"""
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        resultados = Libro.objects.filter(
            Q(titulo__icontains=query) |
            Q(isbn__icontains=query) |
            Q(autor__nombre__icontains=query) |
            Q(autor__apellido__icontains=query)
        ).select_related('autor', 'categoria')[:50]
    
    context = {
        'query': query,
        'resultados': resultados,
        'categorias': Categoria.objects.all(),
        'autores': Autor.objects.all(),
    }
    return render(request, 'libros/busqueda.html', context)

def estadisticas(request):
    """Vista de estadísticas del sistema"""
    from django.contrib.auth.models import User
    import json
    from datetime import timedelta
    
    # Libros por categoría
    libros_por_categoria = Categoria.objects.annotate(
        total=Count('libros')
    ).order_by('-total')
    
    # Datos para gráfico de categorías (convertir a listas de Python)
    categorias_labels = list(libros_por_categoria.values_list('nombre', flat=True))
    categorias_data = list(libros_por_categoria.values_list('total', flat=True))
    
    # Préstamos del último mes (por día)
    hoy = date.today()
    hace_30_dias = hoy - timedelta(days=30)
    
    prestamos_labels = []
    prestamos_data = []
    for i in range(30):
        dia = hace_30_dias + timedelta(days=i)
        prestamos_del_dia = Prestamo.objects.filter(
            fecha_prestamo=dia
        ).count()
        prestamos_labels.append(dia.strftime('%d/%m'))
        prestamos_data.append(prestamos_del_dia)
    
    # Autores más prestados
    autores_prestados = Autor.objects.annotate(
        total_prestamos=Count('libros__prestamos')
    ).order_by('-total_prestamos')[:10]
    
    # Libros más populares
    libros_populares = Libro.objects.annotate(
        total_prestamos=Count('prestamos')
    ).order_by('-total_prestamos')[:10]
    
    context = {
        'total_libros': Libro.objects.count(),
        'prestamos_activos': Prestamo.objects.filter(estado='activo').count(),
        'total_usuarios': User.objects.count(),
        'libros_disponibles': Libro.objects.filter(stock_disponible__gt=0).count(),
        'libros_por_categoria': libros_por_categoria,
        # Convertir a JSON para JavaScript (usar json.dumps)
        'categorias_labels': json.dumps(categorias_labels),
        'categorias_data': json.dumps(categorias_data),
        'prestamos_labels': json.dumps(prestamos_labels),
        'prestamos_data': json.dumps(prestamos_data),
        'top_autores': autores_prestados,
        'top_libros': libros_populares,
    }
    return render(request, 'libros/estadisticas.html', context)

@login_required
def mi_cuenta(request):
    """Vista de perfil de usuario"""
    prestamos_activos = Prestamo.objects.filter(
        usuario=request.user,
        estado='activo'
    ).select_related('libro', 'libro__autor')
    
    historial_prestamos = Prestamo.objects.filter(
        usuario=request.user
    ).exclude(estado='activo').select_related('libro')[:20]
    
    context = {
        'prestamos_activos': prestamos_activos,
        'historial_prestamos': historial_prestamos,
    }
    return render(request, 'libros/mi_cuenta.html', context)

@login_required
def solicitar_prestamo(request, libro_id):
    """Vista para solicitar un préstamo"""
    libro = get_object_or_404(Libro, id=libro_id)
    
    if request.method == 'POST':
        dias = int(request.POST.get('dias', 14))
        fecha_devolucion = date.today() + timedelta(days=dias)
        
        if libro.stock_disponible > 0:
            prestamo = Prestamo.objects.create(
                libro=libro,
                usuario=request.user,
                fecha_devolucion_esperada=fecha_devolucion,
                estado='activo'
            )
            
            # Reducir stock
            libro.stock_disponible -= 1
            libro.save()
            
            return redirect('mi_cuenta')
    
    context = {'libro': libro}
    return render(request, 'libros/solicitar_prestamo.html', context)

@login_required
def renovar_prestamo(request, prestamo_id):
    """Vista para renovar un préstamo"""
    prestamo = get_object_or_404(Prestamo, id=prestamo_id, usuario=request.user)
    
    if prestamo.estado == 'activo':
        # Añadir 14 días más
        prestamo.fecha_devolucion_esperada += timedelta(days=14)
        prestamo.estado = 'renovado'
        prestamo.save()
    
    return redirect('mi_cuenta')