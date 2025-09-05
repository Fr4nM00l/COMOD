# Configuración del Sistema COMOD

## Pasos para configurar la aplicación:

### 1. Crear archivo .env
Crear un archivo `.env` en la carpeta `python_app/` con el siguiente contenido:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password_aqui
DB_NAME=clinicaodontologica
DB_PORT=3306
SECRET_KEY=tu_clave_secreta_muy_segura_cambiar_en_produccion
PORT=5000
```

### 2. Configurar Base de Datos
1. Crear una base de datos MySQL llamada `clinicaodontologica`
2. Importar el archivo `clinicaodontologica.sql`:
```bash
mysql -u root -p clinicaodontologica < clinicaodontologica.sql
```

### 3. Instalar Dependencias
```bash
cd python_app
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Usuarios de Prueba

### Secretarios:
- Laura Martínez (lauram / sec123)
- Verónica Gómez (verog / sec456)

### Odontólogos:
- Dr. Juan Pérez (juanp / odo123)
- Dra. María López (marial / odo456)

## Problemas Corregidos

1. ✅ Agregada dependencia Flask-Moment faltante
2. ✅ Corregido template secretario_dashboard.html para usar base.html
3. ✅ Actualizado requirements.txt con todas las dependencias necesarias
4. ✅ Verificadas rutas de templates en app.py

## Notas Importantes

- Asegúrate de que MySQL esté ejecutándose
- Verifica que la base de datos `clinicaodontologica` exista
- El archivo `.env` es necesario para la configuración de la base de datos
