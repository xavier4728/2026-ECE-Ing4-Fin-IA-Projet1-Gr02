# groupe-JVX/src/strategy_genes.py
import random

def get_gene_ranges():
    """
    Définit les plages de paramètres autorisées (L'ADN de la stratégie).
    CORRECTION EVOLIA : Plages restreintes pour éviter les solutions dégénérées.
    """
    return {
        # MOYENNES MOBILES : Séparation forcée pour garantir la logique de tendance
        # SMA Fast (Rapide) : Doit être réactive (5 à 40 jours)
        'SMA_F': {'min': 5, 'max': 40, 'step': 1},
        
        # SMA Slow (Lente) : Doit être une tendance de fond (50 à 200 jours)
        # On commence à 50 pour éviter que SMA_F >= SMA_S
        'SMA_S': {'min': 50, 'max': 200, 'step': 5},

        # RSI : Logique de Mean Reversion forcée
        # Période standard
        'RSI_P': {'min': 10, 'max': 20, 'step': 1},
        
        # Seuil Achat (LO) : Forcé en zone de survente (20-45). 
        # L'IA ne pourra plus choisir 65 pour "ne rien faire".
        'RSI_LO': {'min': 20, 'max': 45, 'step': 1},
        
        # Seuil Vente (UP) : Forcé en zone de surachat (70-90)
        'RSI_UP': {'min': 70, 'max': 90, 'step': 1},

        # GESTION DU RISQUE (Risk Management)
        # Stop Loss (%) : On laisse une certaine respiration (1% à 10%)
        'SL': {'min': 0.01, 'max': 0.10, 'step': 0.005},
        
        # Take Profit (%) : On vise des ratios R:R > 1 (2% à 20%)
        'TP': {'min': 0.02, 'max': 0.20, 'step': 0.005}
    }

def generate_individual():
    """Génère un individu aléatoire respectant les contraintes"""
    ranges = get_gene_ranges()
    individual = {}
    
    for gene, params in ranges.items():
        if isinstance(params['min'], int):
            individual[gene] = random.randrange(params['min'], params['max'] + 1, params['step'])
        else:
            # Pour les float (SL/TP)
            steps = int((params['max'] - params['min']) / params['step'])
            individual[gene] = params['min'] + (random.randint(0, steps) * params['step'])
            
    return individual