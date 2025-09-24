# CHANGELOG - COMOD

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Sistema de respaldo para templates antiguos
- Documentación de respaldo en `templates/backup/README.md`

### Changed
- Movido `secretario_dashboard_old.html` a carpeta de respaldo
- Actualizada documentación de correcciones

### Fixed
- Eliminadas opciones inapropiadas para secretarios en lista de pacientes
- Removidos botones "Ver Historia" y "Crear Turno" de vista de secretario

## [2025-09-24] - Refactorización Mayor

### Added
- **Servicios de Negocio** (`services.py`):
  - `PatientService` - Operaciones CRUD para pacientes
  - `AppointmentService` - Operaciones CRUD para turnos
  - `DentistService` - Operaciones para odontólogos
  - `ClinicalHistoryService` - Operaciones para historias clínicas
  - `OdontogramaService` - Operaciones para odontogramas

- **Utilidades de Base de Datos** (`db_utils.py`):
  - `get_db_cursor()` - Context manager para operaciones de solo lectura
  - `get_db_cursor_with_commit()` - Context manager para operaciones con commit

- **Utilidades Comunes** (`utils.py`):
  - `format_time_from_timedelta()` - Formateo de tiempo
  - `validate_appointment_datetime()` - Validación de fechas
  - `create_success_response()` - Respuestas JSON de éxito
  - `create_error_response()` - Respuestas JSON de error

- **Decoradores de Autorización** (`decorators.py`):
  - `require_secretario` - Verificación de rol secretario
  - `require_odontologo` - Verificación de rol odontólogo

- **Macros Jinja2** (`templates/macros/`):
  - `common.html` - Macros para elementos comunes
  - `patient.html` - Macros para formularios de pacientes
  - `appointment.html` - Macros para formularios de turnos

- **CSS y JS Centralizados**:
  - `static/css/common.css` - Estilos comunes
  - `static/js/common.js` - JavaScript común
  - `templates/base_improved.html` - Template base mejorado

### Changed
- **Refactorización completa de `app.py`**:
  - Reducido de ~1424 líneas a ~717 líneas (50% menos código)
  - Eliminado código repetitivo de manejo de conexiones
  - Implementado uso de decoradores para autorización
  - Implementado uso de servicios para operaciones de base de datos
  - Estandarizado respuestas JSON
  - Simplificado manejo de errores

- **Templates refactorizados**:
  - `templates/sections/pacientes.html` - Usando macros Jinja2
  - `templates/sections/pacientes_section.html` - Usando macros Jinja2
  - `templates/sections/pacientes_refactored.html` - Ejemplo de refactorización

### Fixed
- Manejo seguro de conexiones de base de datos
- Rollback automático en caso de errores
- Verificación de autorización centralizada
- Respuestas JSON estandarizadas
- Formato de tiempo consistente

### Removed
- Código duplicado de manejo de conexiones
- Lógica repetitiva de verificación de roles
- Código repetitivo de respuestas JSON
- Funciones JavaScript duplicadas

## [2025-09-23] - Correcciones Iniciales

### Added
- Archivo `.env` con configuración de base de datos
- `Flask-Moment==1.0.5` a requirements.txt

### Fixed
- Template `secretario_dashboard.html` reestructurado para usar `base.html`
- 65+ iconos migrados de Font Awesome a Bootstrap Icons
- Problemas de formato de fechas con Flask-Moment
- Configuración de base de datos verificada

### Changed
- Estructura de templates para usar herencia correcta
- Iconos consistentes en toda la aplicación
- Formato de fechas usando métodos nativos de Python

## [2025-09-22] - Versión Inicial

### Added
- Aplicación Flask básica
- Sistema de autenticación
- Dashboards para odontólogos y secretarios
- Gestión de pacientes, turnos, historias clínicas y odontogramas
- Sistema de turnos online
- Base de datos MySQL con datos de prueba

---

## Notas de Versión

### Convenciones de Documentación:
- **Added**: Nuevas funcionalidades
- **Changed**: Cambios en funcionalidades existentes
- **Deprecated**: Funcionalidades que serán removidas en futuras versiones
- **Removed**: Funcionalidades removidas
- **Fixed**: Corrección de bugs
- **Security**: Mejoras de seguridad

### Formato de Fechas:
- `[YYYY-MM-DD]` - Fechas de release
- `[Unreleased]` - Cambios pendientes de release

### Enlaces Útiles:
- [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Documentación del Proyecto](./README.md)
- [Correcciones Realizadas](./CORRECCIONES_REALIZADAS.md)
- [Refactorización](./REFACTORING.md)
