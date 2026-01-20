"""
Genetic Algorithm Core Module using DEAP.
"""
import random
import numpy as np
import warnings
from deap import base, creator, tools, algorithms
from src.strategy_genes import decode_chromosome
from src.backtest_runner import run_backtest
from src.config import Config

# On masque les warnings de calcul sur les infinis
warnings.filterwarnings("ignore")

# 1. Setup DEAP Fitness and Individual
if not hasattr(creator, "FitnessMulti"):
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))

if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMulti)

def eval_genome(individual, data):
    """
    Evaluation function wrapper.
    Must be top-level for Windows multiprocessing pickling.
    """
    try:
        params = decode_chromosome(individual)
        # Run backtest
        profit, drawdown = run_backtest(params, data)
        return (profit, drawdown)
    except Exception:
        return (-100.0, 100.0)

# --- STATISTIQUES CORRIGÉES (Gèrent des scalaires uniquement) ---
def stats_mean(ind_fits):
    # ind_fits est maintenant une liste de floats (Profit uniquement)
    valid_vals = [x for x in ind_fits if np.isfinite(x)]
    return np.mean(valid_vals) if valid_vals else 0.0

def stats_std(ind_fits):
    valid_vals = [x for x in ind_fits if np.isfinite(x)]
    return np.std(valid_vals) if valid_vals else 0.0

def stats_min(ind_fits):
    valid_vals = [x for x in ind_fits if np.isfinite(x)]
    return np.min(valid_vals) if valid_vals else -100.0

def stats_max(ind_fits):
    valid_vals = [x for x in ind_fits if np.isfinite(x)]
    return np.max(valid_vals) if valid_vals else -100.0


class GAEcosystem:
    """
    Manages the Genetic Algorithm evolution process.
    """
    
    def __init__(self, data):
        self.data = data
        self.toolbox = base.Toolbox()
        self._setup_toolbox()
        
    def _setup_toolbox(self):
        """Register genetic operators."""
        bounds = Config.GENE_BOUNDS
        
        self.toolbox.register("attr_sma_f", random.randint, *bounds['SMA_F'])
        self.toolbox.register("attr_sma_s", random.randint, *bounds['SMA_S'])
        self.toolbox.register("attr_rsi_p", random.randint, *bounds['RSI_P'])
        self.toolbox.register("attr_rsi_up", random.randint, *bounds['RSI_UP'])
        self.toolbox.register("attr_rsi_lo", random.randint, *bounds['RSI_LO'])
        self.toolbox.register("attr_sl", random.uniform, *bounds['SL'])
        self.toolbox.register("attr_tp", random.uniform, *bounds['TP'])
        
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                            (self.toolbox.attr_sma_f, self.toolbox.attr_sma_s,
                             self.toolbox.attr_rsi_p, self.toolbox.attr_rsi_up,
                             self.toolbox.attr_rsi_lo, self.toolbox.attr_sl,
                             self.toolbox.attr_tp), n=1)
                             
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("evaluate", eval_genome, data=self.data)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self._custom_mutation)
        self.toolbox.register("select", tools.selNSGA2)
        
    def _custom_mutation(self, individual, indpb=0.2):
        """Custom mutation handling mix of int and float."""
        for i in range(len(individual)):
            if random.random() < indpb:
                if i < 5: # Integer genes
                    individual[i] = int(individual[i] + random.randint(-5, 5))
                    if individual[i] < 5: individual[i] = 5
                else: # Float genes
                    individual[i] += random.gauss(0, 0.02)
                    if individual[i] < 0.01: individual[i] = 0.01
        return individual,

    def run_evolution(self, population_size=Config.GA_POPULATION, generations=Config.GA_GENERATIONS, verbose=True):
        """Run the evolution loop."""
        
        pop = self.toolbox.population(n=population_size)
        
        # --- CORRECTION MAJEURE ICI ---
        # On ne passe que l'index [0] (Le Profit) aux statistiques.
        # Cela évite l'erreur "ambiguous truth value" car on traite des nombres simples, pas des couples.
        stats = tools.Statistics(lambda ind: ind.fitness.values[0])
        
        stats.register("avg", stats_mean)
        stats.register("std", stats_std)
        stats.register("min", stats_min)
        stats.register("max", stats_max)
        
        pop, logbook = algorithms.eaSimple(pop, self.toolbox, 
                                         cxpb=Config.GA_CXPB, 
                                         mutpb=Config.GA_MUTPB, 
                                         ngen=generations, 
                                         stats=stats, 
                                         verbose=verbose)
                                         
        return pop, logbook