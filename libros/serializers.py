from rest_framework import serializers
from .models import Libro, Autor, Categoria, Editorial, Prestamo

class AutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Autor
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 
                  'nacionalidad', 'biografia', 'fecha_nacimiento']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class EditorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editorial
        fields = ['id', 'nombre', 'pais', 'sitio_web']

class LibroSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.nombre_completo', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    editorial_nombre = serializers.CharField(source='editorial.nombre', read_only=True)
    
    class Meta:
        model = Libro
        fields = [
            'id', 'titulo', 'isbn', 'descripcion', 'fecha_publicacion',
            'numero_paginas', 'idioma', 'stock_total', 'stock_disponible',
            'estado', 'autor', 'autor_nombre', 'categoria', 'categoria_nombre',
            'editorial', 'editorial_nombre', 'fecha_registro'
        ]
        read_only_fields = ['fecha_registro']

class PrestamoSerializer(serializers.ModelSerializer):
    libro_titulo = serializers.CharField(source='libro.titulo', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Prestamo
        fields = [
            'id', 'libro', 'libro_titulo', 'usuario', 'usuario_nombre',
            'fecha_prestamo', 'fecha_devolucion_esperada', 'fecha_devolucion_real',
            'estado', 'notas'
        ]
        read_only_fields = ['fecha_prestamo']