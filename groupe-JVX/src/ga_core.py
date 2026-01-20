# groupe-JVX/src/ga_core.py
import random
import numpy as np
from deap import base, creator, tools, algorithms
from .strategy_genes import generate_individual, get_gene_ranges
from .backtest_runner import run_backtest_with_params

# Configuration DEAP
# On maximise le Profit (et potentiellement on pourrait ajouter le Sharpe Ratio)
creator.create("FitnessMax", base.Fitness, weights=(1.0,)) 
creator.create("Individual", dict, fitness=creator.FitnessMax)

def get_toolbox(data_path):
    toolbox = base.Toolbox()

    # Génération des individus via notre fichier strategy_genes corrigé
    toolbox.register("individual", tools.initIterate, creator.Individual, generate_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Opérateurs génétiques
    toolbox.register("mate", tools.cxTwoPoint) # Croisement
    toolbox.register("mutate", mutate_individual, indpb=0.2) # Mutation
    toolbox.register("select", tools.selTournament, tournsize=3) # Sélection
    
    # La fonction d'évaluation critique
    toolbox.register("evaluate", lambda ind: evaluate_logic(ind, data_path))

    return toolbox

def mutate_individual(individual, indpb):
    """Mutation personnalisée qui respecte les plages de strategy_genes"""
    ranges = get_gene_ranges()
    for gene in individual:
        if random.random() < indpb:
            params = ranges[gene]
            # Mutation simple : on tire une nouvelle valeur dans la plage
            if isinstance(params['min'], int):
                 individual[gene] = random.randrange(params['min'], params['max'] + 1, params['step'])
            else:
                 steps = int((params['max'] - params['min']) / params['step'])
                 individual[gene] = params['min'] + (random.randint(0, steps) * params['step'])
    return individual,

def evaluate_logic(individual, data_path):
    """
    Fonction de fitness (Score)
    CORRECTION EVOLIA : Pénalité stricte pour l'inactivité.
    """
    # 1. Vérification de cohérence (Double sécurité)
    if individual['SMA_F'] >= individual['SMA_S']:
        return -100.0, # Pénalité immédiate si Fast >= Slow

    # 2. Lancement du backtest
    stats = run_backtest_with_params(data_path, individual)
    
    # 3. Récupération des métriques
    profit = stats['Return [%]']
    trades = stats['# Trades']
    max_dd = stats['Max. Drawdown [%]']

    # 4. PENALITÉ D'INACTIVITÉ (Le correctif majeur)
    # Si moins de 10 trades sur 2 ans, la stratégie est considérée comme nulle.
    if trades < 10:
        return -50.0, # Score artificiellement bas pour éliminer ces gènes
    
    # 5. Pénalité de risque (Optionnel : on n'aime pas les gros drawdowns)
    if max_dd > 30: # Si drawdown > 30%
        profit -= 20 # On enlève 20% de performance au score

    return profit,

def run_genetic_algo(data_path, pop_size=50, n_gen=10):
    toolbox = get_toolbox(data_path)
    pop = toolbox.population(n=pop_size)
    
    # Statistiques pour les logs
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)
    
    print(f"--- Démarrage Algorithme Génétique (Pop: {pop_size}, Gen: {n_gen}) ---")
    
    # Lancement de l'évolution
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, 
                                       ngen=n_gen, stats=stats, verbose=True)
    
    best_ind = tools.selBest(pop, 1)[0]
    return best_ind, logbook