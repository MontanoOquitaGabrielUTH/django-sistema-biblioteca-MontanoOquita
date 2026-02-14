from django.shortcuts import render
from libros.models import Libro, Autor, Categoria, Prestamo

def home(request):
    """Vista de la página principal"""
    context = {
        'total_libros': Libro.objects.count(),
        'total_autores': Autor.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_prestamos': Prestamo.objects.filter(estado='activo').count(),
    }
    return render(request, 'home.html', context)

def ejemplos_rest(request):
    return render(request, 'ejemplos_rest.html')

def ejemplos_soap(request):
    return render(request, 'ejemplos_soap.html')

def ejemplos_admin(request):
    return render(request, 'ejemplos_admin.html')