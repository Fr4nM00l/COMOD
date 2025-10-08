# 📧 Configuración de Email para COMOD

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la carpeta `python_app` con la siguiente configuración:

```env
# Configuración SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com

# Configuración de la clínica
CLINIC_NAME=Clínica Odontológica COMOD
CLINIC_ADDRESS=Dirección de la Clínica
CLINIC_PHONE=+54 11 1234-5678
CLINIC_EMAIL=info@clinica.com
```

### 3. Configuración para Gmail

Si usas Gmail, necesitas:

1. **Habilitar la verificación en 2 pasos** en tu cuenta de Google
2. **Generar una contraseña de aplicación**:
   - Ve a tu cuenta de Google → Seguridad
   - Busca "Contraseñas de aplicaciones"
   - Genera una nueva contraseña para "Mail"
   - Usa esa contraseña en `MAIL_PASSWORD`

### 4. Otros proveedores SMTP

#### Outlook/Hotmail:
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

#### Yahoo:
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

## 🔧 Funcionalidades Implementadas

### ✅ Email de Confirmación
- Se envía automáticamente cuando se crea un turno
- Incluye todos los detalles del turno
- Diseño profesional y responsive
- Información de contacto de la clínica

### ✅ Integración Completa
- **Turnos del secretario**: Email automático al crear turno
- **Turnos online**: Email automático al reservar turno
- **Manejo de errores**: No falla la creación del turno si hay error de email

### ✅ Template Profesional
- Diseño responsive para móviles
- Información completa del turno
- Datos de contacto de la clínica
- Instrucciones importantes para el paciente

## 🧪 Pruebas

### Probar el sistema:
1. **Configurar email** según las instrucciones anteriores
2. **Crear un turno** desde el secretario o online
3. **Verificar** que llegue el email de confirmación
4. **Revisar logs** en la consola para confirmar envío

### Logs esperados:
```
✅ Appointment created with ID: 123
📧 Email de confirmación enviado a paciente@email.com
```

## 🛠️ Solución de Problemas

### Error: "Configuración de email no encontrada"
- Verificar que el archivo `.env` existe
- Verificar que las variables están correctamente configuradas

### Error: "Authentication failed"
- Verificar usuario y contraseña
- Para Gmail: usar contraseña de aplicación, no la contraseña normal

### Error: "Connection refused"
- Verificar que el servidor SMTP y puerto son correctos
- Verificar conexión a internet

## 📝 Notas Importantes

- **El sistema no falla** si hay problemas con el email
- **Los turnos se crean normalmente** aunque falle el envío
- **Los errores se registran** en la consola para debugging
- **Solo se envía email** si el paciente tiene email registrado

## 🔮 Futuras Mejoras

- Email de recordatorio (24h antes)
- Email de cancelación
- Plantillas personalizables
- Estadísticas de emails enviados

