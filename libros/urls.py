from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para API REST
router = DefaultRouter()
router.register(r'libros', views.LibroViewSet)
router.register(r'autores', views.AutorViewSet)
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'editoriales', views.EditorialViewSet)
router.register(r'prestamos', views.PrestamoViewSet)

urlpatterns = [
    # API REST
    path('', include(router.urls)),
    
    # Vistas tradicionales
    path('index/', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('libro/<int:libro_id>/', views.detalle_libro, name='detalle_libro'),
    path('busqueda/', views.busqueda, name='busqueda'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('solicitar-prestamo/<int:libro_id>/', views.solicitar_prestamo, name='solicitar_prestamo'),
    path('renovar-prestamo/<int:prestamo_id>/', views.renovar_prestamo, name='renovar_prestamo'),]