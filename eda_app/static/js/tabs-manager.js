// Gestion des onglets et navigation
class TabsManager {
    constructor(ajaxLoader) {
        this.ajaxLoader = ajaxLoader;
        this.activeTab = 'general';
        this.loadedTabs = new Set(['general']); // L'onglet général est déjà chargé
        this.datasetId = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Écouter les clics sur les boutons d'onglets
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = button.getAttribute('data-tab');
                if (tabName) {
                    this.showTab(tabName);
                }
            });
        });
    }
    
    async showTab(tabName) {
        if (this.activeTab === tabName) return;
        
        try {
            // Cacher tous les contenus d'onglets
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            // Désactiver tous les boutons d'onglets
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active', 'text-blue-600', 'border-blue-500');
                button.classList.add('text-gray-500', 'border-transparent');
            });
            
            // Activer le bouton sélectionné
            const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
            if (activeButton) {
                activeButton.classList.remove('text-gray-500', 'border-transparent');
                activeButton.classList.add('active', 'text-blue-600', 'border-blue-500');
            }
            
            // Charger le contenu si nécessaire
            if (!this.loadedTabs.has(tabName)) {
                await this.loadTabContent(tabName);
                this.loadedTabs.add(tabName);
            }
            
            // Afficher le contenu
            const content = document.getElementById(`tab-${tabName}`);
            if (content) {
                content.classList.remove('hidden');
            }
            
            this.activeTab = tabName;
            
        } catch (error) {
            console.error('Erreur lors du changement d\'onglet:', error);
            Utils.showNotification('Erreur lors du chargement de l\'onglet', 'error');
        }
    }
    
    async loadTabContent(tabName) {
        const containerId = `tab-${tabName}`;
        const loaderId = `${tabName}-loader`;
        const contentId = `${tabName}-content`;
        
        // Afficher le loader
        this.showLoader(loaderId, contentId);
        
        try {
            let data;
            switch (tabName) {
                case 'statistics':
                    data = await this.ajaxLoader.loadStatistics(this.datasetId);
                    this.renderStatistics(contentId, data);
                    break;
                    
                case 'distributions':
                    data = await this.ajaxLoader.loadDistributions(this.datasetId);
                    this.renderDistributions(contentId, data);
                    break;
                    
                case 'correlations':
                    data = await this.ajaxLoader.loadCorrelations(this.datasetId);
                    this.renderCorrelations(contentId, data);
                    break;
                    
                default:
                    throw new Error(`Onglet non reconnu: ${tabName}`);
            }
            
            // Cacher le loader et afficher le contenu
            this.hideLoader(loaderId, contentId);
            
        } catch (error) {
            console.error(`Erreur lors du chargement de l'onglet ${tabName}:`, error);
            this.showError(loaderId, contentId, error.message);
        }
    }
    
    showLoader(loaderId, contentId) {
        const loader = document.getElementById(loaderId);
        const content = document.getElementById(contentId);
        
        if (loader) loader.classList.remove('hidden');
        if (content) content.classList.add('hidden');
    }
    
    hideLoader(loaderId, contentId) {
        const loader = document.getElementById(loaderId);
        const content = document.getElementById(contentId);
        
        if (loader) loader.classList.add('hidden');
        if (content) content.classList.remove('hidden');
    }
    
    showError(loaderId, contentId, message) {
        const loader = document.getElementById(loaderId);
        const content = document.getElementById(contentId);
        
        if (loader) {
            loader.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Erreur de chargement</h3>
                    <p class="text-gray-600">${message}</p>
                    <button onclick="location.reload()" class="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                        Réessayer
                    </button>
                </div>
            `;
        }
    }
    
    setDatasetId(datasetId) {
        this.datasetId = datasetId;
    }
    
    // Méthodes de rendu (à implémenter selon les besoins)
    renderStatistics(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        let html = `
            <div class="bg-gray-50 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <i class="fas fa-calculator mr-2 text-blue-600"></i>
                    Statistiques Descriptives
                </h3>
        `;
        
        if (data.descriptive_stats) {
            html += `
                <div class="bg-white rounded-lg shadow p-6 mb-6">
                    <h4 class="text-md font-semibold text-gray-700 mb-4">Statistiques Générales</h4>
                    <div class="overflow-x-auto">
                        <table class="min-w-full table-auto">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Statistique</th>
            `;
            
            // En-têtes des colonnes
            Object.keys(data.descriptive_stats).forEach(column => {
                html += `<th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">${column}</th>`;
            });
            
            html += `
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
            `;
            
            // Lignes de données
            Object.entries(data.descriptive_stats).forEach(([stat, values]) => {
                html += `<tr class="hover:bg-gray-50">`;
                html += `<td class="px-4 py-2 font-medium text-gray-900">${stat}</td>`;
                Object.values(values).forEach(value => {
                    html += `<td class="px-4 py-2 text-sm text-gray-600">${Utils.formatNumber(value)}</td>`;
                });
                html += `</tr>`;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        if (data.column_stats) {
            html += `
                <div class="bg-white rounded-lg shadow p-6">
                    <h4 class="text-md font-semibold text-gray-700 mb-4">Statistiques Détaillées - ${data.selected_column}</h4>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            `;
            
            Object.entries(data.column_stats).forEach(([stat, value]) => {
                html += `
                    <div class="bg-gray-50 rounded p-3">
                        <p class="text-xs text-gray-500 uppercase font-medium">${stat}</p>
                        <p class="text-lg font-semibold text-gray-800">${Utils.formatNumber(value)}</p>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
        container.innerHTML = html;
    }
    
    renderDistributions(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        let html = `
            <div class="bg-gray-50 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <i class="fas fa-chart-bar mr-2 text-purple-600"></i>
                    Distributions des Variables
                </h3>
        `;
        
        // Variables numériques
        if (data.numeric_distributions && Object.keys(data.numeric_distributions).length > 0) {
            html += `
                <div class="mb-8">
                    <h4 class="text-md font-semibold text-gray-700 mb-4 flex items-center">
                        <i class="fas fa-hashtag mr-2 text-blue-600"></i>
                        Variables Numériques
                    </h4>
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            `;
            
            Object.entries(data.numeric_distributions).forEach(([column, distData]) => {
                if (distData.histogram) {
                    html += `
                        <div class="bg-white rounded-lg shadow p-4">
                            <h5 class="font-medium text-gray-800 mb-3">${column}</h5>
                            <img src="data:image/png;base64,${distData.histogram}" alt="Histogramme ${column}" class="w-full h-auto">
                        </div>
                    `;
                }
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        // Variables catégorielles
        if (data.categorical_distributions && Object.keys(data.categorical_distributions).length > 0) {
            html += `
                <div>
                    <h4 class="text-md font-semibold text-gray-700 mb-4 flex items-center">
                        <i class="fas fa-tags mr-2 text-purple-600"></i>
                        Variables Catégorielles
                    </h4>
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            `;
            
            Object.entries(data.categorical_distributions).forEach(([column, distData]) => {
                if (distData.bar_chart) {
                    html += `
                        <div class="bg-white rounded-lg shadow p-4">
                            <h5 class="font-medium text-gray-800 mb-3">${column}</h5>
                            <img src="data:image/png;base64,${distData.bar_chart}" alt="Graphique en barres ${column}" class="w-full h-auto">
                        </div>
                    `;
                }
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
        container.innerHTML = html;
    }
    
    renderCorrelations(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        let html = `
            <div class="bg-gray-50 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <i class="fas fa-project-diagram mr-2 text-green-600"></i>
                    Matrice de Corrélations
                </h3>
        `;
        
        if (data.correlation_matrix) {
            html += `
                <div class="bg-white rounded-lg shadow p-6 mb-6">
                    <h4 class="text-md font-semibold text-gray-700 mb-4">Matrice de Corrélations</h4>
                    <div class="overflow-x-auto">
                        <table class="min-w-full table-auto">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Variable</th>
            `;
            
            // En-têtes des colonnes
            Object.keys(data.correlation_matrix).forEach(column => {
                html += `<th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">${column}</th>`;
            });
            
            html += `
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
            `;
            
            // Lignes de données
            Object.entries(data.correlation_matrix).forEach(([row, correlations]) => {
                html += `<tr class="hover:bg-gray-50">`;
                html += `<td class="px-4 py-2 font-medium text-gray-900">${row}</td>`;
                Object.values(correlations).forEach(value => {
                    const colorClass = value >= 0.7 ? 'text-green-600' : value >= 0.5 ? 'text-blue-600' : value >= 0.3 ? 'text-yellow-600' : 'text-gray-600';
                    html += `<td class="px-4 py-2 text-sm ${colorClass} font-medium">${Utils.formatNumber(value)}</td>`;
                });
                html += `</tr>`;
            });
            
            html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        if (data.correlation_pairs && data.correlation_pairs.length > 0) {
            html += `
                <div class="bg-white rounded-lg shadow p-6">
                    <h4 class="text-md font-semibold text-gray-700 mb-4">Corrélations Significatives</h4>
                    <div class="space-y-3">
            `;
            
            data.correlation_pairs.forEach(pair => {
                const strengthColor = pair.strength === 'forte' ? 'text-red-600' : pair.strength === 'modérée' ? 'text-orange-600' : 'text-yellow-600';
                const directionIcon = pair.direction === 'positive' ? '↗' : '↘';
                
                html += `
                    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                            <span class="font-medium text-gray-800">${pair.variable1}</span>
                            <span class="text-gray-500 mx-2">×</span>
                            <span class="font-medium text-gray-800">${pair.variable2}</span>
                        </div>
                        <div class="flex items-center space-x-3">
                            <span class="text-sm ${strengthColor} font-medium">${pair.strength}</span>
                            <span class="text-sm text-gray-600">${directionIcon}</span>
                            <span class="font-semibold text-gray-800">${Utils.formatNumber(pair.correlation)}</span>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
        container.innerHTML = html;
    }
}