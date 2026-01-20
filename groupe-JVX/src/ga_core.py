# groupe-JVX/src/ga_core.py
import random
import numpy as np
from deap import base, creator, tools, algorithms
from .strategy_genes import generate_individual, get_gene_ranges, mutate_individual
from .backtest_runner import run_backtest_with_params
from .config import Config

# Configuration DEAP
if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", dict, fitness=creator.FitnessMax)

class GAEcosystem:
    def __init__(self, data):
        self.data = data
        self.toolbox = base.Toolbox()
        self._setup_toolbox()

    def _setup_toolbox(self):
        self.toolbox.register("individual", tools.initIterate, creator.Individual, generate_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", mutate_individual, indpb=Config.GA_MUTPB)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self._evaluate_individual)

    def _evaluate_individual(self, individual):
        # 1. Cohérence
        if individual['SMA_F'] >= individual['SMA_S']:
            return -100.0,

        # 2. Backtest (Data est déjà un DataFrame ici)
        try:
            stats = run_backtest_with_params(self.data, individual)
            
            profit = stats['Return [%]']
            trades = stats['# Trades']
            max_dd = stats['Max. Drawdown [%]']

            # 3. Pénalités
            if trades < 5: return -50.0, 
            if max_dd > 30: profit -= (max_dd - 30)

            return profit,

        except Exception:
            return -100.0,

    def run_evolution(self, verbose=True):
        pop = self.toolbox.population(n=Config.GA_POPULATION)
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        if verbose:
            print(f"--- GA Start: Pop {Config.GA_POPULATION}, Gen {Config.GA_GENERATIONS} ---")

        pop, logbook = algorithms.eaSimple(
            pop, 
            self.toolbox, 
            cxpb=Config.GA_CXPB, 
            mutpb=Config.GA_MUTPB, 
            ngen=Config.GA_GENERATIONS, 
            stats=stats, 
            verbose=verbose
        )
        
        return pop, logbook