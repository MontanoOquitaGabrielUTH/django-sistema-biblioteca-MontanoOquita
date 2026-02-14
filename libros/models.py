from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Autor(models.Model):
    """Modelo para autores de libros"""
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=50, blank=True)
    biografia = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Editorial(models.Model):
    """Modelo para editoriales"""
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=50)
    sitio_web = models.URLField(blank=True)
    fecha_fundacion = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Editorial"
        verbose_name_plural = "Editoriales"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Modelo para categorías de libros"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Libro(models.Model):
    """Modelo principal para libros"""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('reservado', 'Reservado'),
        ('mantenimiento', 'En Mantenimiento'),
    ]
    
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros')
    editorial = models.ForeignKey(Editorial, on_delete=models.SET_NULL, null=True, related_name='libros')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='libros')
    fecha_publicacion = models.DateField()
    numero_paginas = models.IntegerField()
    idioma = models.CharField(max_length=50, default='Español')
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    stock_total = models.IntegerField(default=1)
    stock_disponible = models.IntegerField(default=1)
    ubicacion_fisica = models.CharField(max_length=50, blank=True, help_text="Ej: Estante A-12")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['titulo']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"
    
    def esta_disponible(self):
        """Verifica si el libro está disponible para préstamo"""
        return self.estado == 'disponible' and self.stock_disponible > 0


class Prestamo(models.Model):
    """Modelo para préstamos de libros"""
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('vencido', 'Vencido'),
        ('renovado', 'Renovado'),
    ]
    
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prestamos')
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    renovaciones = models.IntegerField(default=0)
    multa = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']
    
    def __str__(self):
        return f"{self.libro.titulo} - {self.usuario.username} ({self.estado})"
    
    def esta_vencido(self):
        """Verifica si el préstamo está vencido"""
        from datetime import date
        return self.estado == 'activo' and self.fecha_devolucion_esperada < date.today()