// Gestion des requêtes AJAX et loaders
class AjaxLoader {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    showLoader(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-12">
            <div class="relative">
                <div class="w-14 h-14 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                <i class="fas fa-sync-alt text-blue-500 text-2xl animate-pulse"></i>
                </div>
            </div>
            <span class="mt-4 text-gray-700 font-medium text-lg">Veuillez patienter, chargement...</span>
            </div>
        `;
    }
    
    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">Erreur de chargement</h3>
                <p class="text-gray-600">${message}</p>
                <button onclick="location.reload()" class="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                    Réessayer
                </button>
            </div>
        `;
    }
    
    async loadStatistics(datasetId, selectedColumn = null) {
        try {
            let url = `${this.baseUrl}/dataset/${datasetId}/statistics/`;
            if (selectedColumn) {
                url += `?column=${encodeURIComponent(selectedColumn)}`;
            }
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': Utils.getCsrfToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`Erreur lors du chargement des statistiques: ${error.message}`);
        }
    }
    
    async loadDistributions(datasetId) {
        try {
            const response = await fetch(`${this.baseUrl}/dataset/${datasetId}/distributions/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': Utils.getCsrfToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`Erreur lors du chargement des distributions: ${error.message}`);
        }
    }
    
    async loadCorrelations(datasetId) {
        try {
            const response = await fetch(`${this.baseUrl}/dataset/${datasetId}/correlations/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': Utils.getCsrfToken(),
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            throw new Error(`Erreur lors du chargement des corrélations: ${error.message}`);
        }
    }
}