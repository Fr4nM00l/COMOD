# COMOD - Sistema de Gestión de Centro Odontológico

## Descripción
COMOD es un sistema integral de gestión para centros odontológicos que permite administrar pacientes, turnos, historias clínicas y odontogramas de manera eficiente y organizada.

## Características Principales

### 🔐 Sistema de Autenticación
- Login diferenciado para odontólogos y secretarios
- Control de acceso basado en roles
- Sesiones seguras

### 👥 Gestión de Pacientes
- Registro de nuevos pacientes
- Edición de información personal
- Búsqueda y filtrado de pacientes
- Gestión de contactos de emergencia

### 📅 Gestión de Turnos
- Creación y programación de citas
- Asignación de odontólogos a pacientes
- Estados de turnos (pendiente, en curso, completado, cancelado)
- Filtrado por fecha y estado

### 📋 Historias Clínicas
- Registro completo de antecedentes médicos
- Alergias y medicamentos
- Información de obra social
- Historial de visitas

### 🦷 Odontogramas
- Visualización de estado dental
- Registro de afecciones por diente
- Catálogo de procedimientos disponibles
- Seguimiento de tratamientos

### 🏥 Catálogo de Procedimientos
- Base de datos de procedimientos dentales
- Códigos SNOMED para estandarización
- Información de duración y costos
- Estado activo/inactivo

## Requisitos del Sistema

### Software
- Python 3.8 o superior
- MySQL 5.7+ o MariaDB 10.2+
- Navegador web moderno

### Dependencias Python
- Flask 2.3.3
- mysql-connector-python 8.1.0
- python-dotenv 1.0.0
- Werkzeug 2.3.7

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd COMOD-main
```

### 2. Configurar Base de Datos
1. Crear una base de datos MySQL llamada `clinicaodontologica`
2. Importar el archivo `clinicaodontologica.sql`:
```bash
mysql -u root -p clinicaodontologica < clinicaodontologica.sql
```

### 3. Configurar Variables de Entorno
Crear un archivo `.env` en la carpeta `python_app/`:
```env
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=clinicaodontologica
DB_PORT=3306
SECRET_KEY=tu_clave_secreta_muy_segura
PORT=5000
```

### 4. Instalar Dependencias Python
```bash
cd python_app
pip install -r requirements.txt
```

### 5. Ejecutar la Aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura de la Base de Datos

### Tablas Principales
- **paciente**: Información personal de los pacientes
- **odontologo**: Datos de los profesionales
- **secretario**: Personal administrativo
- **historiaclinica**: Antecedentes médicos
- **odontograma**: Evaluaciones dentales
- **detallediente**: Dientes específicos evaluados
- **afeccion**: Catálogo de afecciones dentales
- **detalleafeccion**: Relación diente-afección
- **procedimientos**: Catálogo de tratamientos
- **detalleprocedimiento**: Procedimientos aplicados por diente
- **detalleturno**: Programación de citas

### Relaciones Clave
- Paciente → Historia Clínica → Odontograma → Detalle Diente
- Diente → Afecciones (detalleafeccion)
- Diente → Procedimientos (detalleprocedimiento)
- Odontólogo ↔ Paciente (detalleturno)

## Uso del Sistema

### Acceso como Secretario
1. Ir a la página de login
2. Seleccionar rol "Secretario"
3. Ingresar credenciales (ej: lauram / sec123)

### Funcionalidades del Secretario
- **Dashboard**: Vista general con estadísticas
- **Pacientes**: Gestión completa de pacientes
- **Turnos**: Programación y administración de citas
- **Historias Clínicas**: Registro de antecedentes médicos
- **Odontogramas**: Gestión de evaluaciones dentales

### Acceso como Odontólogo
1. Ir a la página de login
2. Seleccionar rol "Odontólogo"
3. Ingresar credenciales (ej: juanp / odo123)

### Funcionalidades del Odontólogo
- **Dashboard**: Próximos turnos del día
- Acceso a historias clínicas de pacientes
- Gestión de odontogramas

## Datos de Prueba

### Usuarios Predefinidos
- **Secretarios**:
  - Laura Martínez (lauram / sec123)
  - Verónica Gómez (verog / sec456)
- **Odontólogos**:
  - Dr. Juan Pérez (juanp / odo123)
  - Dra. María López (marial / odo456)

### Pacientes de Ejemplo
- Sofía Ruiz (DNI: 40123456)
- Diego Ramírez (DNI: 38987654)
- María Estévez (DNI: 38223344)

## Características Técnicas

### Frontend
- HTML5 + CSS3 + JavaScript
- Bootstrap 5 para diseño responsivo
- Font Awesome para iconografía
- Moment.js para manejo de fechas

### Backend
- Flask (Python)
- MySQL/MariaDB como base de datos
- Arquitectura MVC
- API REST para operaciones CRUD

### Seguridad
- Autenticación por sesiones
- Validación de roles
- Sanitización de datos
- Protección CSRF

## Mantenimiento y Actualizaciones

### Backup de Base de Datos
```bash
mysqldump -u root -p clinicaodontologica > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Logs de la Aplicación
Los logs se muestran en la consola durante el desarrollo. Para producción, configurar logging apropiado.

### Actualizaciones
1. Hacer backup de la base de datos
2. Actualizar código fuente
3. Ejecutar migraciones de base de datos si las hay
4. Reiniciar la aplicación

## Soporte y Contacto

Para soporte técnico o consultas sobre el sistema:
- Revisar la documentación de la API
- Verificar logs de errores
- Contactar al equipo de desarrollo

## Licencia

Este proyecto es propiedad del Centro Odontológico COMOD y está destinado para uso interno.

---

**Versión**: 1.0.0  
**Última Actualización**: Diciembre 2024  
**Desarrollado por**: Equipo de Desarrollo COMOD
