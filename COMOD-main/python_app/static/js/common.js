/**
 * Funciones comunes para la aplicación COMOD
 */

// Utilidades para formularios
const FormUtils = {
    // Limpiar errores de validación
    clearValidationErrors: function() {
        const errorElements = document.querySelectorAll('.invalid-feedback');
        errorElements.forEach(el => el.textContent = '');
        
        const inputElements = document.querySelectorAll('.is-invalid');
        inputElements.forEach(el => el.classList.remove('is-invalid'));
    },

    // Mostrar error de validación
    showValidationError: function(fieldName, message) {
        const field = document.getElementById(fieldName);
        const errorElement = document.getElementById(fieldName + 'Error');
        
        if (field && errorElement) {
            field.classList.add('is-invalid');
            errorElement.textContent = message;
        }
    },

    // Validar email
    validateEmail: function(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailPattern.test(email);
    },

    // Validar DNI
    validateDNI: function(dni) {
        return /^\d{7,8}$/.test(dni);
    },

    // Obtener datos del formulario
    getFormData: function(formId) {
        const form = document.getElementById(formId);
        if (!form) return {};
        
        const formData = new FormData(form);
        return Object.fromEntries(formData);
    },

    // Llenar formulario con datos
    fillForm: function(formId, data) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key] || '';
            }
        });
    }
};

// Utilidades para alertas
const AlertUtils = {
    // Mostrar alerta de éxito
    showSuccess: function(message, container = null) {
        this.showAlert(message, 'success', container);
    },

    // Mostrar alerta de error
    showError: function(message, container = null) {
        this.showAlert(message, 'danger', container);
    },

    // Mostrar alerta de información
    showInfo: function(message, container = null) {
        this.showAlert(message, 'info', container);
    },

    // Mostrar alerta de advertencia
    showWarning: function(message, container = null) {
        this.showAlert(message, 'warning', container);
    },

    // Mostrar alerta genérica
    showAlert: function(message, type = 'info', container = null) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="bi bi-${this.getIcon(type)} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const targetContainer = container || document.querySelector('.card-body') || document.body;
        targetContainer.insertBefore(alertDiv, targetContainer.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    // Obtener icono según tipo de alerta
    getIcon: function(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
};

// Utilidades para modales
const ModalUtils = {
    // Mostrar modal
    show: function(modalId) {
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        modal.show();
    },

    // Ocultar modal
    hide: function(modalId) {
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        if (modal) {
            modal.hide();
        }
    },

    // Resetear formulario del modal
    resetForm: function(modalId, formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
            FormUtils.clearValidationErrors();
        }
    }
};

// Utilidades para tablas
const TableUtils = {
    // Buscar en tabla
    searchTable: function(searchInputId, tableBodyId) {
        const searchTerm = document.getElementById(searchInputId).value.toLowerCase();
        const rows = document.querySelectorAll(`#${tableBodyId} tr`);
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    },

    // Ordenar tabla
    sortTable: function(tableId, columnIndex, ascending = true) {
        const table = document.getElementById(tableId);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();
            
            if (ascending) {
                return aText.localeCompare(bText);
            } else {
                return bText.localeCompare(aText);
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    }
};

// Utilidades para fechas
const DateUtils = {
    // Formatear fecha para input date
    formatDateForInput: function(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toISOString().split('T')[0];
    },

    // Formatear fecha para mostrar
    formatDateForDisplay: function(date) {
        if (!date) return 'No especificada';
        const d = new Date(date);
        return d.toLocaleDateString('es-ES');
    },

    // Formatear hora para mostrar
    formatTimeForDisplay: function(time) {
        if (!time) return 'No especificada';
        if (typeof time === 'string') return time;
        return time.toString().substr(0, 5);
    },

    // Validar fecha futura
    isFutureDate: function(date) {
        const today = new Date();
        const inputDate = new Date(date);
        return inputDate >= today;
    }
};

// Utilidades para API
const ApiUtils = {
    // Realizar petición GET
    get: async function(url) {
        try {
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error en GET:', error);
            throw error;
        }
    },

    // Realizar petición POST
    post: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error en POST:', error);
            throw error;
        }
    },

    // Realizar petición PUT
    put: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Error en PUT:', error);
            throw error;
        }
    },

    // Realizar petición DELETE
    delete: async function(url) {
        try {
            const response = await fetch(url, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            console.error('Error en DELETE:', error);
            throw error;
        }
    }
};

// Utilidades para loading
const LoadingUtils = {
    // Mostrar loading en botón
    showButtonLoading: function(buttonId, text = 'Cargando...') {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
        }
    },

    // Ocultar loading en botón
    hideButtonLoading: function(buttonId, originalText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    },

    // Mostrar loading en contenedor
    showContainerLoading: function(containerId, message = 'Cargando...') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2">${message}</p>
                </div>
            `;
        }
    }
};

// Inicialización común
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Actualizar fecha actual
    const currentDateElement = document.getElementById('current-date');
    if (currentDateElement) {
        currentDateElement.textContent = new Date().toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
});

// Exportar utilidades para uso global
window.FormUtils = FormUtils;
window.AlertUtils = AlertUtils;
window.ModalUtils = ModalUtils;
window.TableUtils = TableUtils;
window.DateUtils = DateUtils;
window.ApiUtils = ApiUtils;
window.LoadingUtils = LoadingUtils;
