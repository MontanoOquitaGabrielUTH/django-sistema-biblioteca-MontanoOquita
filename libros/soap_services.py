"""
Servicios SOAP para el Sistema de Biblioteca
"""
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Boolean, DateTime, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from libros.models import Libro, Autor, Categoria, Editorial, Prestamo
from django.contrib.auth.models import User


# ===== MODELOS COMPLEJOS SOAP =====

class AutorModel(ComplexModel):
    """Modelo SOAP para Autor"""
    id = Integer
    nombre = Unicode
    apellido = Unicode
    nacionalidad = Unicode
    biografia = Unicode


class CategoriaModel(ComplexModel):
    """Modelo SOAP para Categoría"""
    id = Integer
    nombre = Unicode
    descripcion = Unicode


class EditorialModel(ComplexModel):
    """Modelo SOAP para Editorial"""
    id = Integer
    nombre = Unicode
    pais = Unicode
    sitio_web = Unicode


class LibroModel(ComplexModel):
    """Modelo SOAP para Libro"""
    id = Integer
    titulo = Unicode
    isbn = Unicode
    autor_nombre = Unicode
    editorial_nombre = Unicode
    categoria_nombre = Unicode
    fecha_publicacion = Unicode
    numero_paginas = Integer
    idioma = Unicode
    descripcion = Unicode
    estado = Unicode
    stock_total = Integer
    stock_disponible = Integer
    ubicacion_fisica = Unicode
    fecha_registro = DateTime
    ultima_actualizacion = DateTime


class LibroDetalladoModel(ComplexModel):
    """Modelo SOAP extendido para Libro con relaciones"""
    id = Integer
    titulo = Unicode
    isbn = Unicode
    numero_paginas = Integer
    idioma = Unicode
    descripcion = Unicode
    estado = Unicode
    stock_total = Integer
    stock_disponible = Integer
    ubicacion_fisica = Unicode
    fecha_publicacion = Unicode
    fecha_registro = DateTime
    ultima_actualizacion = DateTime
    # Objetos completos de relaciones
    autor = AutorModel
    editorial = EditorialModel
    categoria = CategoriaModel


class PrestamoModel(ComplexModel):
    """Modelo SOAP para Préstamo"""
    id = Integer
    libro_titulo = Unicode
    usuario_nombre = Unicode
    fecha_prestamo = DateTime
    fecha_devolucion_esperada = Unicode
    fecha_devolucion_real = Unicode
    estado = Unicode
    multa = Unicode


class ResultadoOperacion(ComplexModel):
    """Modelo para respuestas de operaciones"""
    exito = Boolean
    mensaje = Unicode
    id = Integer

# ===== SERVICIOS SOAP =====

class BibliotecaService(ServiceBase):
    """
    Servicios SOAP para gestión de biblioteca digital
    """
    
    # ===== SERVICIOS DE LIBROS =====
    
    @rpc(Integer, _returns=LibroDetalladoModel)
    def obtener_libro(ctx, libro_id):
        """
        Obtiene información completa de un libro por ID
        """
        try:
            libro = Libro.objects.select_related('autor', 'editorial', 'categoria').get(id=libro_id)
            
            # Crear modelo de autor
            autor_model = AutorModel(
                id=libro.autor.id,
                nombre=libro.autor.nombre,
                apellido=libro.autor.apellido,
                nacionalidad=libro.autor.nacionalidad or '',
                biografia=libro.autor.biografia or ''
            )
            
            # Crear modelo de editorial
            editorial_model = EditorialModel(
                id=libro.editorial.id if libro.editorial else 0,
                nombre=libro.editorial.nombre if libro.editorial else 'Sin editorial',
                pais=libro.editorial.pais if libro.editorial else '',
                sitio_web=libro.editorial.sitio_web if libro.editorial else ''
            )
            
            # Crear modelo de categoría
            categoria_model = CategoriaModel(
                id=libro.categoria.id if libro.categoria else 0,
                nombre=libro.categoria.nombre if libro.categoria else 'Sin categoría',
                descripcion=libro.categoria.descripcion if libro.categoria else ''
            )
            
            return LibroDetalladoModel(
                id=libro.id,
                titulo=libro.titulo,
                isbn=libro.isbn,
                numero_paginas=libro.numero_paginas,
                idioma=libro.idioma,
                descripcion=libro.descripcion or '',
                estado=libro.estado,
                stock_total=libro.stock_total,
                stock_disponible=libro.stock_disponible,
                ubicacion_fisica=libro.ubicacion_fisica or '',
                fecha_publicacion=str(libro.fecha_publicacion),
                fecha_registro=libro.fecha_registro,
                ultima_actualizacion=libro.ultima_actualizacion,
                autor=autor_model,
                editorial=editorial_model,
                categoria=categoria_model
            )
        except Libro.DoesNotExist:
            return None
    
    @rpc(_returns=Array(LibroModel))
    def listar_libros(ctx):
        """Lista todos los libros disponibles"""
        libros = Libro.objects.select_related('autor', 'editorial', 'categoria').all()
        resultado = []
        
        for libro in libros:
            resultado.append(LibroModel(
                id=libro.id,
                titulo=libro.titulo,
                isbn=libro.isbn,
                autor_nombre=f"{libro.autor.nombre} {libro.autor.apellido}",
                editorial_nombre=libro.editorial.nombre if libro.editorial else 'Sin editorial',
                categoria_nombre=libro.categoria.nombre if libro.categoria else 'Sin categoría',
                fecha_publicacion=str(libro.fecha_publicacion),
                numero_paginas=libro.numero_paginas,
                idioma=libro.idioma,
                descripcion=libro.descripcion or '',
                estado=libro.estado,
                stock_total=libro.stock_total,
                stock_disponible=libro.stock_disponible,
                ubicacion_fisica=libro.ubicacion_fisica or '',
                fecha_registro=libro.fecha_registro,
                ultima_actualizacion=libro.ultima_actualizacion
            ))
        
        return resultado
    
    @rpc(Unicode, _returns=Array(LibroModel))
    def buscar_libros_por_titulo(ctx, titulo):
        """Busca libros por título (búsqueda parcial)"""
        libros = Libro.objects.filter(titulo__icontains=titulo).select_related('autor', 'editorial', 'categoria')
        resultado = []
        
        for libro in libros:
            resultado.append(LibroModel(
                id=libro.id,
                titulo=libro.titulo,
                isbn=libro.isbn,
                autor_nombre=f"{libro.autor.nombre} {libro.autor.apellido}",
                editorial_nombre=libro.editorial.nombre if libro.editorial else 'Sin editorial',
                categoria_nombre=libro.categoria.nombre if libro.categoria else 'Sin categoría',
                fecha_publicacion=str(libro.fecha_publicacion),
                numero_paginas=libro.numero_paginas,
                idioma=libro.idioma,
                descripcion=libro.descripcion or '',
                estado=libro.estado,
                stock_total=libro.stock_total,
                stock_disponible=libro.stock_disponible,
                ubicacion_fisica=libro.ubicacion_fisica or '',
                fecha_registro=libro.fecha_registro,
                ultima_actualizacion=libro.ultima_actualizacion
            ))
        
        return resultado
    
    @rpc(Unicode, _returns=Array(LibroModel))
    def buscar_libros_por_autor(ctx, autor_apellido):
        """Busca libros por apellido del autor"""
        libros = Libro.objects.filter(
            autor__apellido__icontains=autor_apellido
        ).select_related('autor', 'editorial', 'categoria')
        
        resultado = []
        for libro in libros:
            resultado.append(LibroModel(
                id=libro.id,
                titulo=libro.titulo,
                isbn=libro.isbn,
                autor_nombre=f"{libro.autor.nombre} {libro.autor.apellido}",
                editorial_nombre=libro.editorial.nombre if libro.editorial else 'Sin editorial',
                categoria_nombre=libro.categoria.nombre if libro.categoria else 'Sin categoría',
                fecha_publicacion=str(libro.fecha_publicacion),
                numero_paginas=libro.numero_paginas,
                idioma=libro.idioma,
                descripcion=libro.descripcion or '',
                estado=libro.estado,
                stock_total=libro.stock_total,
                stock_disponible=libro.stock_disponible,
                ubicacion_fisica=libro.ubicacion_fisica or '',
                fecha_registro=libro.fecha_registro,
                ultima_actualizacion=libro.ultima_actualizacion
            ))
        
        return resultado
    
    @rpc(_returns=Array(LibroModel))
    def listar_libros_disponibles(ctx):
        """Lista solo los libros disponibles para préstamo"""
        libros = Libro.objects.filter(
            estado='disponible',
            stock_disponible__gt=0
        ).select_related('autor', 'editorial', 'categoria')
        
        resultado = []
        for libro in libros:
            resultado.append(LibroModel(
                id=libro.id,
                titulo=libro.titulo,
                isbn=libro.isbn,
                autor_nombre=f"{libro.autor.nombre} {libro.autor.apellido}",
                editorial_nombre=libro.editorial.nombre if libro.editorial else 'Sin editorial',
                categoria_nombre=libro.categoria.nombre if libro.categoria else 'Sin categoría',
                fecha_publicacion=str(libro.fecha_publicacion),
                numero_paginas=libro.numero_paginas,
                idioma=libro.idioma,
                descripcion=libro.descripcion or '',
                estado=libro.estado,
                stock_total=libro.stock_total,
                stock_disponible=libro.stock_disponible,
                ubicacion_fisica=libro.ubicacion_fisica or '',
                fecha_registro=libro.fecha_registro,
                ultima_actualizacion=libro.ultima_actualizacion
            ))
        
        return resultado
    
    @rpc(Unicode, _returns=Array(LibroModel))
    def buscar_libros_por_categoria(ctx, categoria_nombre):
        """Busca libros por categoría"""
        libros = Libro.objects.filter(
            categoria__nombre__icontains=categoria_nombre
        ).select_related('autor', 'editorial', 'categoria')
        
        resultado = []
        for libro in libros:
            resultado.append(LibroModel(
                id=libro.id,
                titulo=libro.titulo,
                isbn=libro.isbn,
                autor_nombre=f"{libro.autor.nombre} {libro.autor.apellido}",
                editorial_nombre=libro.editorial.nombre if libro.editorial else 'Sin editorial',
                categoria_nombre=libro.categoria.nombre if libro.categoria else 'Sin categoría',
                fecha_publicacion=str(libro.fecha_publicacion),
                numero_paginas=libro.numero_paginas,
                idioma=libro.idioma,
                descripcion=libro.descripcion or '',
                estado=libro.estado,
                stock_total=libro.stock_total,
                stock_disponible=libro.stock_disponible,
                ubicacion_fisica=libro.ubicacion_fisica or '',
                fecha_registro=libro.fecha_registro,
                ultima_actualizacion=libro.ultima_actualizacion
            ))
        
        return resultado
    

    # ===== SERVICIOS DE PRÉSTAMOS =====
    
    @rpc(Integer, Integer, Integer, _returns=ResultadoOperacion)
    def crear_prestamo(ctx, libro_id, usuario_id, dias_prestamo):
        """Crea un nuevo préstamo de libro"""
        try:
            libro = Libro.objects.get(id=libro_id)
            usuario = User.objects.get(id=usuario_id)
            
            # Verificar disponibilidad
            if not libro.esta_disponible():
                return ResultadoOperacion(
                    exito=False,
                    mensaje=f"El libro '{libro.titulo}' no está disponible",
                    id=0
                )
            
            # Calcular fecha de devolución
            fecha_devolucion = (datetime.now() + timedelta(days=dias_prestamo)).date()
            
            # Crear préstamo
            prestamo = Prestamo.objects.create(
                libro=libro,
                usuario=usuario,
                fecha_devolucion_esperada=fecha_devolucion,
                estado='activo'
            )
            
            # Actualizar stock del libro
            libro.stock_disponible -= 1
            if libro.stock_disponible == 0:
                libro.estado = 'prestado'
            libro.save()
            
            return ResultadoOperacion(
                exito=True,
                mensaje=f"Préstamo creado exitosamente. Devolver antes del {fecha_devolucion}",
                id=prestamo.id
            )
            
        except Libro.DoesNotExist:
            return ResultadoOperacion(exito=False, mensaje="Libro no encontrado", id=0)
        except User.DoesNotExist:
            return ResultadoOperacion(exito=False, mensaje="Usuario no encontrado", id=0)
        except Exception as e:
            return ResultadoOperacion(exito=False, mensaje=f"Error: {str(e)}", id=0)
    
    @rpc(Integer, _returns=ResultadoOperacion)
    def devolver_libro(ctx, prestamo_id):
        """Registra la devolución de un libro"""
        try:
            prestamo = Prestamo.objects.get(id=prestamo_id)
            
            if prestamo.estado != 'activo':
                return ResultadoOperacion(
                    exito=False,
                    mensaje="El préstamo ya fue devuelto o está inactivo",
                    id=prestamo_id
                )
            
            # Registrar devolución
            from datetime import date
            prestamo.fecha_devolucion_real = date.today()
            prestamo.estado = 'devuelto'
            
            # Calcular multa si está vencido
            if prestamo.esta_vencido():
                dias_retraso = (date.today() - prestamo.fecha_devolucion_esperada).days
                prestamo.multa = dias_retraso * 10.00  # $10 por día
                prestamo.estado = 'vencido'
            
            prestamo.save()
            
            # Actualizar stock del libro
            libro = prestamo.libro
            libro.stock_disponible += 1
            if libro.stock_disponible > 0:
                libro.estado = 'disponible'
            libro.save()
            
            mensaje = f"Libro devuelto exitosamente"
            if prestamo.multa > 0:
                mensaje += f". Multa: ${prestamo.multa}"
            
            return ResultadoOperacion(
                exito=True,
                mensaje=mensaje,
                id=prestamo_id
            )
            
        except Prestamo.DoesNotExist:
            return ResultadoOperacion(exito=False, mensaje="Préstamo no encontrado", id=0)
        except Exception as e:
            return ResultadoOperacion(exito=False, mensaje=f"Error: {str(e)}", id=0)
    
    @rpc(Integer, _returns=Array(PrestamoModel))
    def obtener_prestamos_usuario(ctx, usuario_id):
        """Obtiene todos los préstamos de un usuario"""
        prestamos = Prestamo.objects.filter(usuario_id=usuario_id).select_related('libro', 'usuario')
        resultado = []
        
        for prestamo in prestamos:
            resultado.append(PrestamoModel(
                id=prestamo.id,
                libro_titulo=prestamo.libro.titulo,
                usuario_nombre=prestamo.usuario.get_full_name() or prestamo.usuario.username,
                fecha_prestamo=prestamo.fecha_prestamo,
                fecha_devolucion_esperada=str(prestamo.fecha_devolucion_esperada),
                fecha_devolucion_real=str(prestamo.fecha_devolucion_real) if prestamo.fecha_devolucion_real else '',
                estado=prestamo.estado,
                multa=str(prestamo.multa)
            ))
        
        return resultado
    
    @rpc(_returns=Array(PrestamoModel))
    def listar_prestamos_activos(ctx):
        """Lista todos los préstamos activos"""
        prestamos = Prestamo.objects.filter(estado='activo').select_related('libro', 'usuario')
        resultado = []
        
        for prestamo in prestamos:
            resultado.append(PrestamoModel(
                id=prestamo.id,
                libro_titulo=prestamo.libro.titulo,
                usuario_nombre=prestamo.usuario.get_full_name() or prestamo.usuario.username,
                fecha_prestamo=prestamo.fecha_prestamo,
                fecha_devolucion_esperada=str(prestamo.fecha_devolucion_esperada),
                fecha_devolucion_real='',
                estado=prestamo.estado,
                multa=str(prestamo.multa)
            ))
        
        return resultado
    
    # ===== SERVICIOS DE AUTORES =====
    
    @rpc(_returns=Array(AutorModel))
    def listar_autores(ctx):
        """Lista todos los autores"""
        autores = Autor.objects.all()
        resultado = []
        
        for autor in autores:
            resultado.append(AutorModel(
                id=autor.id,
                nombre=autor.nombre,
                apellido=autor.apellido,
                nacionalidad=autor.nacionalidad or '',
                biografia=autor.biografia or ''
            ))
        
        return resultado
    
    # ===== SERVICIOS DE CATEGORÍAS =====
    
    @rpc(_returns=Array(CategoriaModel))
    def listar_categorias(ctx):
        """Lista todas las categorías"""
        categorias = Categoria.objects.all()
        resultado = []
        
        for categoria in categorias:
            resultado.append(CategoriaModel(
                id=categoria.id,
                nombre=categoria.nombre,
                descripcion=categoria.descripcion or ''
            ))
        
        return resultado


# ===== CONFIGURACIÓN DE LA APLICACIÓN SOAP =====

soap_app = Application(
    [BibliotecaService],
    tns='biblioteca.soap.services',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# Vista Django para el servicio SOAP
django_soap_application = csrf_exempt(DjangoApplication(soap_app))