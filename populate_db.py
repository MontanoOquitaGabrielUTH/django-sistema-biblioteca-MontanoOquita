"""
Script para poblar la base de datos con datos de prueba
Ejecutar con: python populate_db.py
"""
import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca_project.settings')
django.setup()

from django.contrib.auth.models import User
from libros.models import Autor, Editorial, Categoria, Libro, Prestamo


def crear_usuarios():
    """Crear usuarios de prueba"""
    print("Creando usuarios...")
    
    # Crear superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@biblioteca.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        print("  ✓ Superusuario 'admin' creado (password: admin123)")
    
    # Crear usuarios normales
    usuarios_data = [
        {'username': 'juan_perez', 'email': 'juan@email.com', 'first_name': 'Juan', 'last_name': 'Pérez'},
        {'username': 'maria_lopez', 'email': 'maria@email.com', 'first_name': 'María', 'last_name': 'López'},
        {'username': 'carlos_ruiz', 'email': 'carlos@email.com', 'first_name': 'Carlos', 'last_name': 'Ruiz'},
    ]
    
    for user_data in usuarios_data:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(
                password='user123',
                **user_data
            )
            print(f"  ✓ Usuario '{user_data['username']}' creado")


def crear_autores():
    """Crear autores de prueba"""
    print("\nCreando autores...")
    
    autores_data = [
        {
            'nombre': 'Gabriel',
            'apellido': 'García Márquez',
            'fecha_nacimiento': date(1927, 3, 6),
            'nacionalidad': 'Colombiano',
            'biografia': 'Premio Nobel de Literatura 1982. Autor de Cien años de soledad.'
        },
        {
            'nombre': 'Isabel',
            'apellido': 'Allende',
            'fecha_nacimiento': date(1942, 8, 2),
            'nacionalidad': 'Chilena',
            'biografia': 'Una de las novelistas más leídas en español. Autora de La casa de los espíritus.'
        },
        {
            'nombre': 'Jorge Luis',
            'apellido': 'Borges',
            'fecha_nacimiento': date(1899, 8, 24),
            'nacionalidad': 'Argentino',
            'biografia': 'Uno de los escritores más importantes del siglo XX en lengua española.'
        },
        {
            'nombre': 'Octavio',
            'apellido': 'Paz',
            'fecha_nacimiento': date(1914, 3, 31),
            'nacionalidad': 'Mexicano',
            'biografia': 'Premio Nobel de Literatura 1990. Ensayista y poeta mexicano.'
        },
        {
            'nombre': 'Mario',
            'apellido': 'Vargas Llosa',
            'fecha_nacimiento': date(1936, 3, 28),
            'nacionalidad': 'Peruano',
            'biografia': 'Premio Nobel de Literatura 2010. Autor de La ciudad y los perros.'
        },
    ]
    
    for autor_data in autores_data:
        autor, created = Autor.objects.get_or_create(
            nombre=autor_data['nombre'],
            apellido=autor_data['apellido'],
            defaults=autor_data
        )
        if created:
            print(f"  ✓ Autor '{autor}' creado")


def crear_editoriales():
    """Crear editoriales de prueba"""
    print("\nCreando editoriales...")
    
    editoriales_data = [
        {
            'nombre': 'Editorial Sudamericana',
            'pais': 'Argentina',
            'sitio_web': 'https://www.megustaleer.com.ar',
            'fecha_fundacion': date(1939, 1, 1)
        },
        {
            'nombre': 'Planeta',
            'pais': 'España',
            'sitio_web': 'https://www.planetadelibros.com',
            'fecha_fundacion': date(1949, 1, 1)
        },
        {
            'nombre': 'Alfaguara',
            'pais': 'España',
            'sitio_web': 'https://www.penguinrandomhouse.com',
            'fecha_fundacion': date(1964, 1, 1)
        },
        {
            'nombre': 'Anagrama',
            'pais': 'España',
            'sitio_web': 'https://www.anagrama-ed.es',
            'fecha_fundacion': date(1969, 1, 1)
        },
    ]
    
    for editorial_data in editoriales_data:
        editorial, created = Editorial.objects.get_or_create(
            nombre=editorial_data['nombre'],
            defaults=editorial_data
        )
        if created:
            print(f"  ✓ Editorial '{editorial}' creada")


def crear_categorias():
    """Crear categorías de prueba"""
    print("\nCreando categorías...")
    
    categorias_data = [
        {'nombre': 'Ficción', 'descripcion': 'Novelas y cuentos de ficción literaria'},
        {'nombre': 'Fantasía', 'descripcion': 'Literatura fantástica y de mundos imaginarios'},
        {'nombre': 'Ciencia Ficción', 'descripcion': 'Narrativa especulativa y futurista'},
        {'nombre': 'Romance', 'descripcion': 'Novelas románticas y de amor'},
        {'nombre': 'Misterio', 'descripcion': 'Novelas policiacas y de suspenso'},
        {'nombre': 'Terror', 'descripcion': 'Literatura de horror y terror'},
        {'nombre': 'Aventura', 'descripcion': 'Historias de aventuras y acción'},
        {'nombre': 'Historia', 'descripcion': 'Libros de historia y biografías'},
        {'nombre': 'Poesía', 'descripcion': 'Obras poéticas y antologías'},
        {'nombre': 'Ensayo', 'descripcion': 'Ensayos literarios y filosóficos'},
    ]
    
    for categoria_data in categorias_data:
        categoria, created = Categoria.objects.get_or_create(
            nombre=categoria_data['nombre'],
            defaults=categoria_data
        )
        if created:
            print(f"  ✓ Categoría '{categoria}' creada")


def crear_libros():
    """Crear libros de prueba"""
    print("\nCreando libros...")
    
    # Obtener datos existentes
    garcia_marquez = Autor.objects.get(apellido='García Márquez')
    allende = Autor.objects.get(apellido='Allende')
    borges = Autor.objects.get(apellido='Borges')
    paz = Autor.objects.get(apellido='Paz')
    vargas_llosa = Autor.objects.get(apellido='Vargas Llosa')
    
    sudamericana = Editorial.objects.get(nombre='Editorial Sudamericana')
    planeta = Editorial.objects.get(nombre='Planeta')
    alfaguara = Editorial.objects.get(nombre='Alfaguara')
    
    ficcion = Categoria.objects.get(nombre='Ficción')
    poesia = Categoria.objects.get(nombre='Poesía')
    ensayo = Categoria.objects.get(nombre='Ensayo')
    
    libros_data = [
        {
            'titulo': 'Cien años de soledad',
            'isbn': '9780307474728',
            'autor': garcia_marquez,
            'editorial': sudamericana,
            'categoria': ficcion,
            'fecha_publicacion': date(1967, 5, 30),
            'numero_paginas': 471,
            'idioma': 'Español',
            'descripcion': 'Obra maestra del realismo mágico que narra la historia de la familia Buendía.',
            'estado': 'disponible',
            'stock_total': 5,
            'stock_disponible': 3,
            'ubicacion_fisica': 'Estante A-12'
        },
        {
            'titulo': 'El amor en los tiempos del cólera',
            'isbn': '9780307387738',
            'autor': garcia_marquez,
            'editorial': sudamericana,
            'categoria': ficcion,
            'fecha_publicacion': date(1985, 1, 1),
            'numero_paginas': 368,
            'idioma': 'Español',
            'descripcion': 'Historia de amor que transcurre a lo largo de más de cincuenta años.',
            'estado': 'disponible',
            'stock_total': 3,
            'stock_disponible': 2,
            'ubicacion_fisica': 'Estante A-13'
        },
        {
            'titulo': 'La casa de los espíritus',
            'isbn': '9788401242281',
            'autor': allende,
            'editorial': planeta,
            'categoria': ficcion,
            'fecha_publicacion': date(1982, 1, 1),
            'numero_paginas': 433,
            'idioma': 'Español',
            'descripcion': 'Saga familiar chilena que mezcla lo cotidiano con lo maravilloso.',
            'estado': 'disponible',
            'stock_total': 4,
            'stock_disponible': 4,
            'ubicacion_fisica': 'Estante B-05'
        },
        {
            'titulo': 'Ficciones',
            'isbn': '9780802130303',
            'autor': borges,
            'editorial': sudamericana,
            'categoria': ficcion,
            'fecha_publicacion': date(1944, 1, 1),
            'numero_paginas': 174,
            'idioma': 'Español',
            'descripcion': 'Colección de cuentos que explora temas filosóficos y metafísicos.',
            'estado': 'disponible',
            'stock_total': 3,
            'stock_disponible': 1,
            'ubicacion_fisica': 'Estante C-08'
        },
        {
            'titulo': 'El laberinto de la soledad',
            'isbn': '9786071613578',
            'autor': paz,
            'editorial': sudamericana,
            'categoria': ensayo,
            'fecha_publicacion': date(1950, 1, 1),
            'numero_paginas': 191,
            'idioma': 'Español',
            'descripcion': 'Ensayo sobre la identidad mexicana y latinoamericana.',
            'estado': 'disponible',
            'stock_total': 2,
            'stock_disponible': 2,
            'ubicacion_fisica': 'Estante D-15'
        },
        {
            'titulo': 'La ciudad y los perros',
            'isbn': '9788420412146',
            'autor': vargas_llosa,
            'editorial': alfaguara,
            'categoria': ficcion,
            'fecha_publicacion': date(1963, 1, 1),
            'numero_paginas': 399,
            'idioma': 'Español',
            'descripcion': 'Novela ambientada en un colegio militar de Lima.',
            'estado': 'disponible',
            'stock_total': 4,
            'stock_disponible': 3,
            'ubicacion_fisica': 'Estante E-20'
        },
        {
            'titulo': 'Conversación en La Catedral',
            'isbn': '9788420412153',
            'autor': vargas_llosa,
            'editorial': alfaguara,
            'categoria': ficcion,
            'fecha_publicacion': date(1969, 1, 1),
            'numero_paginas': 729,
            'idioma': 'Español',
            'descripcion': 'Retrato crítico de la sociedad peruana bajo dictadura.',
            'estado': 'disponible',
            'stock_total': 2,
            'stock_disponible': 2,
            'ubicacion_fisica': 'Estante E-21'
        },
    ]
    
    for libro_data in libros_data:
        libro, created = Libro.objects.get_or_create(
            isbn=libro_data['isbn'],
            defaults=libro_data
        )
        if created:
            print(f"  ✓ Libro '{libro.titulo}' creado")


def crear_prestamos():
    """Crear préstamos de prueba"""
    print("\nCreando préstamos...")
    
    # Obtener usuarios y libros
    juan = User.objects.get(username='juan_perez')
    maria = User.objects.get(username='maria_lopez')
    
    cien_anos = Libro.objects.get(isbn='9780307474728')
    ficciones = Libro.objects.get(isbn='9780802130303')
    
    # Crear préstamos
    prestamos_data = [
        {
            'libro': cien_anos,
            'usuario': juan,
            'fecha_devolucion_esperada': date.today() + timedelta(days=14),
            'estado': 'activo'
        },
        {
            'libro': ficciones,
            'usuario': maria,
            'fecha_devolucion_esperada': date.today() + timedelta(days=7),
            'estado': 'activo'
        },
    ]
    
    for prestamo_data in prestamos_data:
        prestamo, created = Prestamo.objects.get_or_create(
            libro=prestamo_data['libro'],
            usuario=prestamo_data['usuario'],
            estado='activo',
            defaults=prestamo_data
        )
        if created:
            # Actualizar stock del libro
            libro = prestamo_data['libro']
            libro.stock_disponible -= 1
            if libro.stock_disponible == 0:
                libro.estado = 'prestado'
            libro.save()
            print(f"  ✓ Préstamo '{prestamo}' creado")


def main():
    """Función principal"""
    print("="*60)
    print("📚 POBLANDO BASE DE DATOS - Sistema de Biblioteca")
    print("="*60)
    
    try:
        crear_usuarios()
        crear_autores()
        crear_editoriales()
        crear_categorias()
        crear_libros()
        crear_prestamos()
        
        print("\n" + "="*60)
        print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print("="*60)
        print("\n📊 Resumen:")
        print(f"  • Usuarios: {User.objects.count()}")
        print(f"  • Autores: {Autor.objects.count()}")
        print(f"  • Editoriales: {Editorial.objects.count()}")
        print(f"  • Categorías: {Categoria.objects.count()}")
        print(f"  • Libros: {Libro.objects.count()}")
        print(f"  • Préstamos: {Prestamo.objects.count()}")
        print("\n🔑 Credenciales de acceso:")
        print("  Admin: username='admin', password='admin123'")
        print("  Usuarios: password='user123'")
        print("\n🌐 Accede al panel de administración en:")
        print("  http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()