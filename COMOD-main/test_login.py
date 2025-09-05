#!/usr/bin/env python3
"""
Script para probar el login de la aplicación COMOD
"""

import requests
import sys

def test_login():
    """Probar el login con credenciales de secretario"""
    print("🔍 Probando login de secretario...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Crear sesión
        session = requests.Session()
        
        # Obtener página de login
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ Error al acceder a la página de login: {response.status_code}")
            return False
        
        print("✅ Página de login accesible")
        
        # Datos de login para secretario
        login_data = {
            'role': 'secretario',
            'username': 'lauram',
            'password': 'sec123'
        }
        
        # Intentar login
        response = session.post(f"{base_url}/", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:  # Redirect después del login exitoso
            print("✅ Login de secretario exitoso")
            
            # Verificar que redirige al dashboard del secretario
            if '/secretario' in response.headers.get('Location', ''):
                print("✅ Redirección al dashboard correcta")
                return True
            else:
                print(f"⚠️  Redirección inesperada: {response.headers.get('Location')}")
                return False
        else:
            print(f"❌ Error en el login: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_odontologo_login():
    """Probar el login con credenciales de odontólogo"""
    print("\n🔍 Probando login de odontólogo...")
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # Datos de login para odontólogo
        login_data = {
            'role': 'odontologo',
            'username': 'juanp',
            'password': 'odo123'
        }
        
        # Intentar login
        response = session.post(f"{base_url}/", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Login de odontólogo exitoso")
            
            # Verificar que redirige al dashboard del odontólogo
            if '/odontologo' in response.headers.get('Location', ''):
                print("✅ Redirección al dashboard correcta")
                return True
            else:
                print(f"⚠️  Redirección inesperada: {response.headers.get('Location')}")
                return False
        else:
            print(f"❌ Error en el login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de login de COMOD...\n")
    
    tests = [
        ("Login Secretario", test_login),
        ("Login Odontólogo", test_odontologo_login),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS DE LOGIN")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ¡Todas las pruebas de login pasaron!")
        print("💡 La aplicación está funcionando correctamente")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
