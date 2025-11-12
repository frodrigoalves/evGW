// Funções auxiliares globais
console.log('Dashboard Jurídico - Grupo Win carregado!');

// Auto-dismiss alerts após 5 segundos
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});
