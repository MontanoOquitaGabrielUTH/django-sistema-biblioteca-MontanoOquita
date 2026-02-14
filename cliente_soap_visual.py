#!/usr/bin/env python3
"""
Cliente SOAP Visual - Sistema de Biblioteca
Ejecuta operaciones y muestra XML en navegador
"""

from zeep import Client, Settings
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
import sys
import webbrowser
import os
import tempfile
from datetime import datetime
from lxml import etree

WSDL_URL = 'http://127.0.0.1:8000/soap/?wsdl'

# Plugin para capturar mensajes SOAP
history = HistoryPlugin()

def crear_cliente():
    """Crea cliente SOAP con configuración optimizada"""
    try:
        settings = Settings(strict=False, xml_huge_tree=True, xsd_ignore_sequence_order=True)
        client = Client(WSDL_URL, settings=settings, plugins=[history])
        return client
    except Exception as e:
        print(f"❌ Error al conectar con el servidor SOAP: {e}")
        print("\n💡 Asegúrate de que el servidor Django esté corriendo:")
        print("   python manage.py runserver")
        sys.exit(1)

def formatear_xml(xml_string):
    """Formatea XML para mejor visualización"""
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(xml_string, parser)
        return etree.tostring(root, pretty_print=True, encoding='unicode')
    except:
        return xml_string

def mostrar_xml_en_navegador(request_xml, response_xml, operacion):
    """Genera HTML con XML SOAP y lo abre en navegador"""
    import html
    
    request_formatted = formatear_xml(request_xml)
    response_formatted = formatear_xml(response_xml)
    
    request_escaped = html.escape(request_formatted)
    response_escaped = html.escape(response_formatted)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>🔍 XML SOAP - {operacion}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; min-height: 100vh; }}
        .container {{ max-width: 1600px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 40px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
        .header .info {{ font-size: 1.1em; opacity: 0.95; margin: 5px 0; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 25px; border-radius: 10px; font-size: 1.5em; margin-bottom: 20px; display: flex; align-items: center; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }}
        .section-title .icon {{ margin-right: 15px; font-size: 1.5em; }}
        .xml-container {{ background: #1e1e1e; border-radius: 10px; padding: 25px; overflow-x: auto; box-shadow: inset 0 2px 10px rgba(0,0,0,0.3); max-height: 600px; overflow-y: auto; }}
        pre {{ margin: 0; color: #d4d4d4; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.95em; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; }}
        .copy-btn {{ background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 1em; margin-top: 15px; transition: all 0.3s; box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3); }}
        .copy-btn:hover {{ background: #45a049; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(76, 175, 80, 0.4); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }}
        .stat-card .value {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .stat-card .label {{ font-size: 0.9em; opacity: 0.9; }}
        .footer {{ text-align: center; padding: 20px; background: #f5f5f5; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Visualizador de XML SOAP</h1>
            <div class="info"><strong>Operación:</strong> {operacion}</div>
            <div class="info"><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div class="info"><strong>Servidor:</strong> {WSDL_URL}</div>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat-card"><div class="value">{len(request_xml)}</div><div class="label">Bytes Request</div></div>
                <div class="stat-card"><div class="value">{len(response_xml)}</div><div class="label">Bytes Response</div></div>
                <div class="stat-card"><div class="value">{request_formatted.count('<')}</div><div class="label">Tags Request</div></div>
                <div class="stat-card"><div class="value">{response_formatted.count('<')}</div><div class="label">Tags Response</div></div>
            </div>
            <div class="section">
                <div class="section-title"><span class="icon">📤</span><span>SOAP Request</span></div>
                <div class="xml-container"><pre id="request-xml">{request_escaped}</pre></div>
                <button class="copy-btn" onclick="copyToClipboard('request-xml')">📋 Copiar Request</button>
            </div>
            <div class="section">
                <div class="section-title"><span class="icon">📥</span><span>SOAP Response</span></div>
                <div class="xml-container"><pre id="response-xml">{response_escaped}</pre></div>
                <button class="copy-btn" onclick="copyToClipboard('response-xml')">📋 Copiar Response</button>
            </div>
        </div>
        <div class="footer">Sistema de Biblioteca - Cliente SOAP Visual<br>Universidad Tecnológica de Hermosillo</div>
    </div>
    <script>
        function copyToClipboard(elementId) {{
            const text = document.getElementById(elementId).textContent;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copiado!';
                btn.style.background = '#2196F3';
                setTimeout(() => {{ btn.textContent = originalText; btn.style.background = '#4CAF50'; }}, 2000);
            }}).catch(err => {{ alert('Error al copiar: ' + err); }});
        }}
    </script>
</body>
</html>
"""
    
    # Guardar HTML en archivo temporal y abrirlo
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(html_content)
        temp_file = f.name
    
    print(f"\n🌐 Abriendo visualizador XML en el navegador...")
    webbrowser.open('file://' + os.path.abspath(temp_file))

def preguntar_ver_xml():
    """Pregunta si desea ver el XML"""
    print("\n" + "="*80)
    respuesta = input("¿Desea ver el XML SOAP en el navegador? (s/n): ").strip().lower()
    return respuesta in ['s', 'si', 'sí', 'y', 'yes']

# ===== FUNCIONES DE OPERACIONES =====

def listar_libros(client):
    """Lista todos los libros"""
    print("\n" + "="*80)
    print("📚 LISTANDO TODOS LOS LIBROS")
    print("="*80)
    
    try:
        result = client.service.listar_libros()
        
        if not result:
            print("\n⚠️  No hay libros registrados en la biblioteca")
            return
        
        print(f"\n✅ Se encontraron {len(result)} libros:\n")
        
        for i, libro in enumerate(result, 1):
            print(f"\n{i}. 📖 {libro.titulo}")
            print(f"   ID: {libro.id}")
            print(f"   📝 ISBN: {libro.isbn}")
            print(f"   ✍️  Autor: {libro.autor_nombre}")
            print(f"   📚 Editorial: {libro.editorial_nombre}")
            print(f"   🏷️  Categoría: {libro.categoria_nombre}")
            print(f"   📅 Publicación: {libro.fecha_publicacion}")
            print(f"   📄 Páginas: {libro.numero_paginas}")
            print(f"   🌐 Idioma: {libro.idioma}")
            print(f"   📊 Estado: {libro.estado}")
            print(f"   📦 Disponibles: {libro.stock_disponible}")
            if libro.ubicacion_fisica:
                print(f"   📍 Ubicación: {libro.ubicacion_fisica}")
            if libro.descripcion:
                print(f"   📖 Descripción: {libro.descripcion[:100]}...")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "listar_libros")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def obtener_libro(client):
    """Obtiene detalles de un libro por ID"""
    print("\n" + "="*80)
    print("🔍 OBTENER LIBRO POR ID")
    print("="*80)
    
    try:
        libro_id = int(input("\nIngrese el ID del libro: "))
        result = client.service.obtener_libro(libro_id)
        
        if not result:
            print(f"\n⚠️  No se encontró libro con ID {libro_id}")
            return
        
        print(f"\n✅ Libro encontrado:\n")
        print(f"📖 {result.titulo}")
        print(f"ID: {result.id}")
        print(f"📝 ISBN: {result.isbn}")
        print(f"\n👤 AUTOR:")
        print(f"   Nombre: {result.autor.nombre} {result.autor.apellido}")
        print(f"   Nacionalidad: {result.autor.nacionalidad}")
        print(f"   Biografía: {result.autor.biografia[:100] if result.autor.biografia else 'N/A'}...")
        print(f"\n🏢 EDITORIAL:")
        print(f"   Nombre: {result.editorial.nombre}")
        print(f"   País: {result.editorial.pais}")
        print(f"   Web: {result.editorial.sitio_web}")
        print(f"\n🏷️  CATEGORÍA:")
        print(f"   Nombre: {result.categoria.nombre}")
        print(f"   Descripción: {result.categoria.descripcion}")
        print(f"\n📄 DETALLES:")
        print(f"   Páginas: {result.numero_paginas}")
        print(f"   Idioma: {result.idioma}")
        print(f"   Publicación: {result.fecha_publicacion}")
        print(f"   Registro: {result.fecha_registro}")
        print(f"   Estado: {result.estado}")
        print(f"   Stock Total: {result.stock_total}")
        print(f"   Stock Disponible: {result.stock_disponible}")
        print(f"   Ubicación: {result.ubicacion_fisica}")
        print(f"\n📖 Descripción:")
        print(f"   {result.descripcion}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, f"obtener_libro (ID: {libro_id})")
            
    except ValueError:
        print("\n❌ Error: Debe ingresar un número válido")
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def buscar_libros_por_titulo(client):
    """Busca libros por título"""
    print("\n" + "="*80)
    print("🔍 BUSCAR LIBROS POR TÍTULO")
    print("="*80)
    
    titulo = input("\nIngrese texto a buscar en el título: ").strip()
    
    if not titulo:
        print("\n❌ Debe ingresar un texto para buscar")
        return
    
    try:
        result = client.service.buscar_libros_por_titulo(titulo)
        
        if not result:
            print(f"\n⚠️  No se encontraron libros con '{titulo}' en el título")
            return
        
        print(f"\n✅ Se encontraron {len(result)} libros:\n")
        
        for i, libro in enumerate(result, 1):
            print(f"{i}. 📖 {libro.titulo}")
            print(f"   Autor: {libro.autor_nombre} | Categoría: {libro.categoria_nombre}")
            print(f"   Estado: {libro.estado} | Disponibles: {libro.stock_disponible}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, f"buscar_libros_por_titulo ('{titulo}')")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def buscar_libros_por_autor(client):
    """Busca libros por apellido del autor"""
    print("\n" + "="*80)
    print("🔍 BUSCAR LIBROS POR AUTOR")
    print("="*80)
    
    apellido = input("\nIngrese el apellido del autor: ").strip()
    
    if not apellido:
        print("\n❌ Debe ingresar un apellido")
        return
    
    try:
        result = client.service.buscar_libros_por_autor(apellido)
        
        if not result:
            print(f"\n⚠️  No se encontraron libros del autor '{apellido}'")
            return
        
        print(f"\n✅ Se encontraron {len(result)} libros:\n")
        
        for i, libro in enumerate(result, 1):
            print(f"{i}. 📖 {libro.titulo}")
            print(f"   Autor: {libro.autor_nombre}")
            print(f"   Categoría: {libro.categoria_nombre} | Año: {libro.fecha_publicacion}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, f"buscar_libros_por_autor ('{apellido}')")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def buscar_libros_por_categoria(client):
    """Busca libros por categoría"""
    print("\n" + "="*80)
    print("🔍 BUSCAR LIBROS POR CATEGORÍA")
    print("="*80)
    
    categoria = input("\nIngrese el nombre de la categoría: ").strip()
    
    if not categoria:
        print("\n❌ Debe ingresar una categoría")
        return
    
    try:
        result = client.service.buscar_libros_por_categoria(categoria)
        
        if not result:
            print(f"\n⚠️  No se encontraron libros en la categoría '{categoria}'")
            return
        
        print(f"\n✅ Se encontraron {len(result)} libros:\n")
        
        for i, libro in enumerate(result, 1):
            print(f"{i}. 📖 {libro.titulo}")
            print(f"   Autor: {libro.autor_nombre}")
            print(f"   Disponibles: {libro.stock_disponible} | Estado: {libro.estado}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, f"buscar_libros_por_categoria ('{categoria}')")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def listar_libros_disponibles(client):
    """Lista libros disponibles"""
    print("\n" + "="*80)
    print("📚 LIBROS DISPONIBLES PARA PRÉSTAMO")
    print("="*80)
    
    try:
        result = client.service.listar_libros_disponibles()
        
        if not result:
            print("\n⚠️  No hay libros disponibles actualmente")
            return
        
        print(f"\n✅ Se encontraron {len(result)} libros disponibles:\n")
        
        for i, libro in enumerate(result, 1):
            print(f"{i}. 📖 {libro.titulo}")
            print(f"   ID: {libro.id} | Autor: {libro.autor_nombre}")
            print(f"   Disponibles: {libro.stock_disponible} unidades")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "listar_libros_disponibles")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def crear_prestamo(client):
    """Crea un nuevo préstamo"""
    print("\n" + "="*80)
    print("➕ CREAR NUEVO PRÉSTAMO")
    print("="*80)
    
    try:
        libro_id = int(input("\nID del libro: "))
        usuario_id = int(input("ID del usuario: "))
        dias = int(input("Días de préstamo (ej: 14): "))
        
        result = client.service.crear_prestamo(libro_id, usuario_id, dias)
        
        if result.exito:
            print(f"\n✅ {result.mensaje}")
            print(f"   ID del préstamo: {result.id}")
        else:
            print(f"\n❌ {result.mensaje}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "crear_prestamo")
            
    except ValueError:
        print("\n❌ Error: Debe ingresar números válidos")
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def devolver_libro(client):
    """Registra devolución de libro"""
    print("\n" + "="*80)
    print("📥 DEVOLVER LIBRO")
    print("="*80)
    
    try:
        prestamo_id = int(input("\nID del préstamo: "))
        
        result = client.service.devolver_libro(prestamo_id)
        
        if result.exito:
            print(f"\n✅ {result.mensaje}")
        else:
            print(f"\n❌ {result.mensaje}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "devolver_libro")
            
    except ValueError:
        print("\n❌ Error: Debe ingresar un número válido")
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def ver_prestamos_usuario(client):
    """Ver préstamos de un usuario"""
    print("\n" + "="*80)
    print("👤 PRÉSTAMOS DE USUARIO")
    print("="*80)
    
    try:
        usuario_id = int(input("\nID del usuario: "))
        
        result = client.service.obtener_prestamos_usuario(usuario_id)
        
        if not result:
            print(f"\n⚠️  El usuario no tiene préstamos registrados")
            return
        
        print(f"\n✅ Se encontraron {len(result)} préstamos:\n")
        
        for i, prestamo in enumerate(result, 1):
            print(f"{i}. 📖 {prestamo.libro_titulo}")
            print(f"   ID: {prestamo.id} | Usuario: {prestamo.usuario_nombre}")
            print(f"   Préstamo: {prestamo.fecha_prestamo}")
            print(f"   Devolución esperada: {prestamo.fecha_devolucion_esperada}")
            if prestamo.fecha_devolucion_real:
                print(f"   Devuelto: {prestamo.fecha_devolucion_real}")
            print(f"   Estado: {prestamo.estado}")
            if prestamo.multa and float(prestamo.multa) > 0:
                print(f"   💰 Multa: ${prestamo.multa}")
            print()
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, f"obtener_prestamos_usuario (ID: {usuario_id})")
            
    except ValueError:
        print("\n❌ Error: Debe ingresar un número válido")
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def listar_prestamos_activos(client):
    """Lista préstamos activos"""
    print("\n" + "="*80)
    print("📋 PRÉSTAMOS ACTIVOS")
    print("="*80)
    
    try:
        result = client.service.listar_prestamos_activos()
        
        if not result:
            print("\n⚠️  No hay préstamos activos")
            return
        
        print(f"\n✅ Se encontraron {len(result)} préstamos activos:\n")
        
        for i, prestamo in enumerate(result, 1):
            print(f"{i}. 📖 {prestamo.libro_titulo}")
            print(f"   Usuario: {prestamo.usuario_nombre}")
            print(f"   Debe devolver: {prestamo.fecha_devolucion_esperada}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "listar_prestamos_activos")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def listar_autores(client):
    """Lista todos los autores"""
    print("\n" + "="*80)
    print("👥 LISTADO DE AUTORES")
    print("="*80)
    
    try:
        result = client.service.listar_autores()
        
        if not result:
            print("\n⚠️  No hay autores registrados")
            return
        
        print(f"\n✅ Se encontraron {len(result)} autores:\n")
        
        for i, autor in enumerate(result, 1):
            print(f"{i}. {autor.nombre} {autor.apellido}")
            print(f"   ID: {autor.id} | Nacionalidad: {autor.nacionalidad}")
            if autor.biografia:
                print(f"   Bio: {autor.biografia[:80]}...")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "listar_autores")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def listar_categorias(client):
    """Lista todas las categorías"""
    print("\n" + "="*80)
    print("🏷️  LISTADO DE CATEGORÍAS")
    print("="*80)
    
    try:
        result = client.service.listar_categorias()
        
        if not result:
            print("\n⚠️  No hay categorías registradas")
            return
        
        print(f"\n✅ Se encontraron {len(result)} categorías:\n")
        
        for i, cat in enumerate(result, 1):
            print(f"{i}. {cat.nombre}")
            print(f"   ID: {cat.id}")
            if cat.descripcion:
                print(f"   Descripción: {cat.descripcion}")
        
        if preguntar_ver_xml():
            request_xml = etree.tostring(history.last_sent['envelope'], encoding='unicode', pretty_print=True)
            response_xml = etree.tostring(history.last_received['envelope'], encoding='unicode', pretty_print=True)
            mostrar_xml_en_navegador(request_xml, response_xml, "listar_categorias")
            
    except Fault as e:
        print(f"\n❌ Error SOAP: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*80)
    print("🏛️  SISTEMA DE BIBLIOTECA - CLIENTE SOAP INTERACTIVO")
    print("="*80)
    print("\n📚 OPERACIONES DE LIBROS:")
    print("  1. Listar todos los libros")
    print("  2. Obtener libro por ID")
    print("  3. Buscar libros por título")
    print("  4. Buscar libros por autor (apellido)")
    print("  5. Buscar libros por categoría")
    print("  6. Listar libros disponibles")
    print("\n📋 OPERACIONES DE PRÉSTAMOS:")
    print("  7. Crear préstamo")
    print("  8. Devolver libro")
    print("  9. Ver préstamos de un usuario")
    print(" 10. Listar préstamos activos")
    print("\n👥 OPERACIONES DE CATÁLOGOS:")
    print(" 11. Listar autores")
    print(" 12. Listar categorías")
    print("\n  0. Salir")
    print("="*80)

def main():
    """Función principal"""
    print("\n🔌 Conectando al servidor SOAP...")
    client = crear_cliente()
    print("✅ Conexión establecida")
    
    operaciones = {
        '1': listar_libros,
        '2': obtener_libro,
        '3': buscar_libros_por_titulo,
        '4': buscar_libros_por_autor,
        '5': buscar_libros_por_categoria,
        '6': listar_libros_disponibles,
        '7': crear_prestamo,
        '8': devolver_libro,
        '9': ver_prestamos_usuario,
        '10': listar_prestamos_activos,
        '11': listar_autores,
        '12': listar_categorias,
    }
    
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '0':
            print("\n👋 ¡Hasta luego!")
            break
        
        if opcion in operaciones:
            operaciones[opcion](client)
        else:
            print("\n❌ Opción inválida")
        
        input("\n⏎ Presione Enter para continuar...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)