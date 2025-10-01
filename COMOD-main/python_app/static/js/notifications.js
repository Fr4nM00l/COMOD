/**
 * Sistema de Notificaciones Personalizado
 * Reemplaza las alertas del navegador con notificaciones elegantes
 */

class NotificationSystem {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Crear contenedor si no existe
        if (!document.getElementById('notification-container')) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    /**
     * Mostrar notificación
     * @param {string} type - Tipo de notificación: success, error, warning, info
     * @param {string} title - Título de la notificación
     * @param {string} message - Mensaje de la notificación
     * @param {number} duration - Duración en milisegundos (0 = no auto-close)
     */
    show(type, title, message, duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Iconos para cada tipo
        const icons = {
            success: '<i class="bi bi-check-circle-fill text-success"></i>',
            error: '<i class="bi bi-exclamation-triangle-fill text-danger"></i>',
            warning: '<i class="bi bi-exclamation-circle-fill text-warning"></i>',
            info: '<i class="bi bi-info-circle-fill text-info"></i>'
        };

        notification.innerHTML = `
            <div class="notification-header">
                <h6 class="notification-title">
                    ${icons[type] || icons.info}
                    ${title}
                </h6>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="bi bi-x"></i>
                </button>
            </div>
            <p class="notification-message">${message}</p>
            ${duration > 0 ? '<div class="notification-progress"></div>' : ''}
        `;

        this.container.appendChild(notification);

        // Auto-close si se especifica duración
        if (duration > 0) {
            setTimeout(() => {
                this.hide(notification);
            }, duration);
        }

        return notification;
    }

    /**
     * Ocultar notificación
     * @param {HTMLElement} notification - Elemento de notificación
     */
    hide(notification) {
        if (notification && notification.parentNode) {
            notification.classList.add('hide');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }

    /**
     * Limpiar todas las notificaciones
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }

    // Métodos de conveniencia
    success(title, message, duration = 5000) {
        return this.show('success', title, message, duration);
    }

    error(title, message, duration = 7000) {
        return this.show('error', title, message, duration);
    }

    warning(title, message, duration = 6000) {
        return this.show('warning', title, message, duration);
    }

    info(title, message, duration = 5000) {
        return this.show('info', title, message, duration);
    }
}

// Instancia global
const notifications = new NotificationSystem();

/**
 * Funciones de conveniencia para reemplazar alertas comunes
 */

// Reemplazar alert() del navegador
function showAlert(message, type = 'info') {
    const titles = {
        success: 'Éxito',
        error: 'Error',
        warning: 'Advertencia',
        info: 'Información'
    };
    
    notifications.show(type, titles[type], message);
}

// Función para confirmaciones personalizadas
function showConfirm(title, message, onConfirm, onCancel = null) {
    const confirmModal = document.createElement('div');
    confirmModal.className = 'modal fade';
    confirmModal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-danger" id="confirm-btn">Confirmar</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(confirmModal);
    
    const modal = new bootstrap.Modal(confirmModal);
    modal.show();

    // Event listeners
    document.getElementById('confirm-btn').addEventListener('click', () => {
        modal.hide();
        if (onConfirm) onConfirm();
        setTimeout(() => {
            document.body.removeChild(confirmModal);
        }, 300);
    });

    confirmModal.addEventListener('hidden.bs.modal', () => {
        if (onCancel) onCancel();
        setTimeout(() => {
            if (document.body.contains(confirmModal)) {
                document.body.removeChild(confirmModal);
            }
        }, 300);
    });
}

/**
 * Funciones específicas para la aplicación COMOD
 */

// Notificación de éxito al eliminar paciente
function showPatientDeletedSuccess(patientName) {
    notifications.success(
        'Paciente Eliminado',
        `El paciente "${patientName}" ha sido eliminado exitosamente.`,
        5000
    );
}

// Notificación de éxito al eliminar turno
function showAppointmentDeletedSuccess(appointmentInfo) {
    notifications.success(
        'Turno Eliminado',
        `El turno del ${appointmentInfo.date} a las ${appointmentInfo.time} ha sido eliminado exitosamente.`,
        5000
    );
}

// Notificación de error al eliminar
function showDeleteError(itemType, errorMessage = '') {
    notifications.error(
        'Error al Eliminar',
        `No se pudo eliminar el ${itemType}. ${errorMessage}`,
        7000
    );
}

// Notificación de éxito al crear/actualizar
function showSaveSuccess(itemType, action = 'guardado') {
    notifications.success(
        `${itemType} ${action.charAt(0).toUpperCase() + action.slice(1)}`,
        `El ${itemType} ha sido ${action} exitosamente.`,
        5000
    );
}

// Notificación de error al crear/actualizar
function showSaveError(itemType, errorMessage = '') {
    notifications.error(
        'Error al Guardar',
        `No se pudo guardar el ${itemType}. ${errorMessage}`,
        7000
    );
}

// Confirmación personalizada para eliminar
function confirmDelete(itemType, itemName, onConfirm) {
    showConfirm(
        `Eliminar ${itemType}`,
        `¿Estás seguro de que deseas eliminar "${itemName}"? Esta acción no se puede deshacer.`,
        onConfirm
    );
}

// Notificación específica para turnos duplicados
function showDuplicateAppointmentError(errorMessage) {
    notifications.error(
        'Turno Duplicado',
        errorMessage,
        8000 // Mostrar por más tiempo para que el usuario pueda leer el mensaje completo
    );
}

// Exportar para uso global
window.notifications = notifications;
window.showAlert = showAlert;
window.showConfirm = showConfirm;
window.showPatientDeletedSuccess = showPatientDeletedSuccess;
window.showAppointmentDeletedSuccess = showAppointmentDeletedSuccess;
window.showDeleteError = showDeleteError;
window.showSaveSuccess = showSaveSuccess;
window.showSaveError = showSaveError;
window.confirmDelete = confirmDelete;
window.showDuplicateAppointmentError = showDuplicateAppointmentError;
