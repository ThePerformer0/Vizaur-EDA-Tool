// Point d'entrée principal pour la page overview
class OverviewApp {
    constructor() {
        this.datasetId = null;
        this.datasetName = null;
        this.ajaxLoader = null;
        this.tabsManager = null;
        
        this.init();
    }
    
    init() {
        // Récupérer l'ID et le nom du dataset depuis les variables globales
        this.datasetId = window.datasetId;
        this.datasetName = window.datasetName;
        
        if (!this.datasetId) {
            console.error('ID du dataset introuvable');
            return;
        }
        
        // Initialiser les composants
        this.ajaxLoader = new AjaxLoader('');  // Base URL vide car URLs relatives
        this.tabsManager = new TabsManager(this.ajaxLoader);
        this.tabsManager.setDatasetId(this.datasetId);
        
        // Initialiser les gestionnaires d'événements
        this.initializeEventListeners();
        
        console.log('OverviewApp initialisé pour le dataset:', this.datasetId, this.datasetName);
    }
    
    initializeEventListeners() {
        // Gestionnaire pour le sélecteur de colonnes (statistiques)
        const columnSelector = document.getElementById('column-selector');
        if (columnSelector) {
            columnSelector.addEventListener('change', () => {
                this.handleColumnSelection();
            });
        }
    }
    
    async handleColumnSelection() {
        const columnSelector = document.getElementById('column-selector');
        const selectedColumn = columnSelector?.value;
        
        if (selectedColumn && this.tabsManager.activeTab === 'statistics') {
            // Recharger les statistiques pour la colonne sélectionnée
            this.tabsManager.loadedTabs.delete('statistics');
            await this.tabsManager.loadTabContent('statistics');
        }
    }
}

// Initialisation au chargement du DOM
document.addEventListener('DOMContentLoaded', function() {
    new OverviewApp();
});