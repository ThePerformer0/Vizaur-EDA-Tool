// Fonctions utilitaires globales
class Utils {
    static getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }
    
    static formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return '--';
        return parseFloat(num).toFixed(decimals);
    }
    
    static showNotification(message, type = 'info') {
        // Toast notification simple
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        } text-white`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}