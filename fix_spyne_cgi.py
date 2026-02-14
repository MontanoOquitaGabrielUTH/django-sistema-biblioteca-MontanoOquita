"""
Script para arreglar el problema del módulo cgi en Spyne para Python 3.13+
El módulo cgi fue eliminado en Python 3.13, este script lo reemplaza con email.message
"""
import os
import sys

def find_spyne_path():
    """Encuentra la ruta del paquete spyne"""
    try:
        import spyne
        return os.path.dirname(spyne.__file__)
    except ImportError:
        print("❌ Error: Spyne no está instalado")
        sys.exit(1)

def patch_wsgi_file(spyne_path):
    """Parchea el archivo wsgi.py que usa cgi"""
    wsgi_file = os.path.join(spyne_path, 'server', 'wsgi.py')
    
    if not os.path.exists(wsgi_file):
        print(f"❌ No se encontró: {wsgi_file}")
        return False
    
    print(f"📝 Parcheando: {wsgi_file}")
    
    with open(wsgi_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar import cgi
    if 'import cgi' in content:
        # Agregar el import de email.message al inicio si no existe
        if 'from email.message import Message' not in content:
            content = content.replace(
                'import cgi',
                'from email.message import Message'
            )
        
        # Reemplazar cgi.parse_header con parse_header_value
        content = content.replace(
            'cgi.parse_header(',
            'parse_header_value('
        )
        
        # Agregar la función parse_header_value si no existe
        if 'def parse_header_value' not in content:
            helper_function = '''

def parse_header_value(value):
    """Parse header value like cgi.parse_header() did"""
    if not value:
        return '', {}
    
    msg = Message()
    msg['content-type'] = value
    params = msg.get_params()
    
    if params:
        maintype = params[0][0]
        pdict = dict(params[1:])
        return maintype, pdict
    else:
        return value.strip(), {}

'''
            # Insertar la función helper después de los imports
            import_end = content.find('\n\nclass') if '\n\nclass' in content else content.find('\n\ndef')
            if import_end != -1:
                content = content[:import_end] + helper_function + content[import_end:]
        
        # Guardar archivo modificado
        with open(wsgi_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo parcheado exitosamente")
        return True
    else:
        print(f"ℹ️  El archivo ya no usa 'import cgi'")
        return False

def patch_soap11_file(spyne_path):
    """Parchea el archivo soap11.py si es necesario"""
    soap11_file = os.path.join(spyne_path, 'protocol', 'soap', 'soap11.py')
    
    if not os.path.exists(soap11_file):
        print(f"⚠️  No se encontró: {soap11_file}")
        return False
    
    print(f"📝 Verificando: {soap11_file}")
    
    with open(soap11_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'import cgi' in content and 'from email.message import Message' not in content:
        content = content.replace(
            'import cgi',
            'from email.message import Message'
        )
        
        # Si se usa cgi.parse_header, agregar la función helper
        if 'cgi.parse_header' in content:
            content = content.replace('cgi.parse_header(', 'parse_header_value(')
            
            helper_function = '''

def parse_header_value(value):
    """Parse header value like cgi.parse_header() did"""
    if not value:
        return '', {}
    
    msg = Message()
    msg['content-type'] = value
    params = msg.get_params()
    
    if params:
        maintype = params[0][0]
        pdict = dict(params[1:])
        return maintype, pdict
    else:
        return value.strip(), {}

'''
            import_end = content.find('\n\nclass') if '\n\nclass' in content else content.find('\n\ndef')
            if import_end != -1:
                content = content[:import_end] + helper_function + content[import_end:]
        
        with open(soap11_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo parcheado exitosamente")
        return True
    else:
        print(f"ℹ️  El archivo no necesita parches")
        return False

def main():
    print("="*70)
    print("🔧 PARCHE PARA SPYNE - Python 3.13+ (Problema del módulo cgi)")
    print("="*70)
    
    spyne_path = find_spyne_path()
    print(f"\n📦 Spyne encontrado en: {spyne_path}")
    print(f"🐍 Python: {sys.version}\n")
    
    patched_count = 0
    
    # Parchear wsgi.py
    if patch_wsgi_file(spyne_path):
        patched_count += 1
    
    print()
    
    # Parchear soap11.py
    if patch_soap11_file(spyne_path):
        patched_count += 1
    
    print("\n" + "="*70)
    if patched_count > 0:
        print(f"✅ {patched_count} archivo(s) parcheado(s) exitosamente")
        print("\n💡 Reinicia el servidor Django para aplicar los cambios:")
        print("   python manage.py runserver")
    else:
        print("ℹ️  No se encontraron archivos que necesiten parches")
    print("="*70)

if __name__ == '__main__':
    main()