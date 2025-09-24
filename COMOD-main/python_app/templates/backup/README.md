# Archivos de Respaldo - Templates

## 📁 Contenido de esta carpeta

Esta carpeta contiene archivos de templates que han sido reemplazados por versiones más nuevas y optimizadas, pero se mantienen como respaldo por seguridad.

## 📋 Archivos en respaldo

### `secretario_dashboard_old.html`
- **Fecha de respaldo**: 24 de septiembre de 2025
- **Razón**: Reemplazado por `secretario_dashboard.html` (versión más limpia y modular)
- **Líneas de código**: 621 líneas
- **Funcionalidades**: Dashboard completo con todas las secciones integradas
- **Estado**: Ya no se usa en la aplicación

## 🔄 ¿Cuándo restaurar?

**Solo restaurar si:**
1. La nueva versión tiene errores críticos
2. Falta alguna funcionalidad específica que estaba en la versión antigua
3. Se necesita comparar implementaciones

## ⚠️ Advertencias

- **NO usar directamente** - la aplicación está configurada para usar la nueva versión
- **Verificar compatibilidad** - puede haber conflictos con el código refactorizado
- **Documentar cambios** - si se restaura, documentar qué se cambió y por qué

## 📝 Notas de migración

### Diferencias principales entre versiones:

| Aspecto | Versión Antigua | Versión Nueva |
|---------|----------------|---------------|
| Estructura | Monolítica (todo en un archivo) | Modular (secciones separadas) |
| Líneas de código | 621 líneas | 142 líneas |
| JavaScript | ~500 líneas integradas | ~200 líneas + archivos externos |
| Mantenibilidad | Baja | Alta |
| Rendimiento | Regular | Mejor |

### Funcionalidades que podrían faltar:
- Algunas validaciones específicas
- Funciones JavaScript personalizadas
- Estilos CSS específicos

## 🛠️ Proceso de restauración

Si necesitas restaurar:

1. **Hacer backup de la versión actual**:
   ```bash
   cp secretario_dashboard.html secretario_dashboard_backup.html
   ```

2. **Restaurar la versión antigua**:
   ```bash
   cp backup/secretario_dashboard_old.html secretario_dashboard.html
   ```

3. **Verificar funcionalidad** y documentar cualquier problema

4. **Considerar migrar** las funcionalidades faltantes a la nueva versión en lugar de mantener la antigua

## 📞 Contacto

Si tienes dudas sobre qué versión usar o necesitas ayuda con la migración, consulta la documentación del proyecto o contacta al equipo de desarrollo.
