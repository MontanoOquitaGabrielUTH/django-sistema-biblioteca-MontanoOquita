// ========== CONFIGURACIÓN GLOBAL ==========
const API_BASE_URL = '/api';
const SEARCH_DEBOUNCE_MS = 300;

// ========== UTILIDADES ==========
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

const showLoading = () => {
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = '⏳ Cargando...';
    document.body.appendChild(loader);
};

const hideLoading = () => {
    const loader = document.querySelector('.loader');
    if (loader) loader.remove();
};

// ========== BÚSQUEDA EN TIEMPO REAL ==========
const searchInput = document.getElementById('search-input');
if (searchInput) {
    const performSearch = async (query) => {
        if (query.length < 3) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/libros/?search=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            updateSearchResults(data.results || data);
        } catch (error) {
            console.error('Error en búsqueda:', error);
        }
    };
    
    const debouncedSearch = debounce(performSearch, SEARCH_DEBOUNCE_MS);
    
    searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });
}

const updateSearchResults = (libros) => {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    if (libros.length === 0) {
        resultsContainer.innerHTML = 'No se encontraron resultados';
        return;
    }
    
    const html = libros.map(libro => `${libro.titulo} ${libro.autor_nombre} ${libro.categoria_nombre} ${libro.stock_disponible > 0 ? 'Disponible' :  'No disponible'} Ver `).join('');
    resultsContainer.innerHTML = html;
};

// ========== FILTROS DINÁMICOS ==========
const filterForm = document.getElementById('filtros-form');
if (filterForm) {
    filterForm.addEventListener('change', (e) => {
        e.preventDefault();
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);
        
        // Recargar con los nuevos parámetros
        window.location.href = `?${params.toString()}`;
    });
}

// ========== SOLICITAR PRÉSTAMO (Envío tradicional con validación) ==========
const prestamoForm = document.querySelector('.prestamo-form');
if (prestamoForm) {
    prestamoForm.addEventListener('submit', function(e) {
        const terminos = prestamoForm.querySelector('input[name="acepto_terminos"]');
        
        if (!terminos || !terminos.checked) {
            e.preventDefault();
            alert('⚠️ Debes aceptar los términos y condiciones');
            return false;
        }
        
        // Permitir el envío normal del formulario (POST tradicional)
        // El formulario se enviará a la URL especificada en el atributo action
        return true;
    });
}

// ========== RENOVAR PRÉSTAMO ==========
document.querySelectorAll('.btn-renovar').forEach(btn => {
    btn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const prestamoId = btn.dataset.prestamoId;
        
        if (!confirm('¿Deseas renovar este préstamo por 14 días más?')) {
            return;
        }
        
        try {
            showLoading();
            
            const response = await fetch(`/renovar-prestamo/${prestamoId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                },
            });
            
            hideLoading();
            
            if (response.ok) {
                showNotification('✅ Préstamo renovado exitosamente', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('❌ No se pudo renovar el préstamo', 'error');
            }
        } catch (error) {
            hideLoading();
            console.error('Error:', error);
            showNotification('❌ Error de conexión', 'error');
        }
    });
});

// ========== NOTIFICACIONES ==========
const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};

// Estilos de notificación (agregar al CSS)
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 5px;
        color: white;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        transform: translateX(400px);
        transition: transform 0.3s;
        z-index: 9999;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        background: #28a745;
    }
    
    .notification-error {
        background: #dc3545;
    }
    
    .notification-info {
        background: #17a2b8;
    }
`;

// ========== CSRF TOKEN ==========
const getCsrfToken = () => {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// ========== CALCULAR FECHA DE DEVOLUCIÓN ==========
const calculateReturnDate = (dias) => {
    const date = new Date();
    date.setDate(date.getDate() + parseInt(dias));
    return date.toISOString().split('T')[0];
};

// ========== ANIMACIONES AL SCROLL ==========
const observeElements = () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.stat-card, .feature-card, .libro-card').forEach(el => {
        observer.observe(el);
    });
};

// ========== GRÁFICOS DE ESTADÍSTICAS ==========
const loadCharts = async () => {
    const categoriasCanvas = document.getElementById('chart-categorias');
    const prestamosCanvas = document.getElementById('chart-prestamos');
    
    if (!categoriasCanvas || !prestamosCanvas) return;
    
    // Aquí se integraría Chart.js
    console.log('Cargar gráficos con Chart.js');
};

// ========== SMOOTH SCROLL ==========
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ========== INICIALIZACIÓN ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Sistema de Biblioteca iniciado');
    observeElements();
    loadCharts();
    
    // Agregar estilos de notificación
    const style = document.createElement('style');
    style.textContent = notificationStyles;
    document.head.appendChild(style);
});

