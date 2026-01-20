"""
Genetic Algorithm Core Module using DEAP.
"""
import random
import numpy as np
from deap import base, creator, tools, algorithms
from src.strategy_genes import decode_chromosome
from src.backtest_runner import run_backtest
from src.config import Config
import multiprocessing

# 1. Setup DEAP Fitness and Individual
# Weights: (Profit: +1.0, Drawdown: -1.0) -> Maximize Profit, Minimize Drawdown
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
        # Attribute generators based on Config ranges
        bounds = Config.GENE_BOUNDS
        
        self.toolbox.register("attr_sma_f", random.randint, *bounds['SMA_F'])
        self.toolbox.register("attr_sma_s", random.randint, *bounds['SMA_S'])
        self.toolbox.register("attr_rsi_p", random.randint, *bounds['RSI_P'])
        self.toolbox.register("attr_rsi_up", random.randint, *bounds['RSI_UP'])
        self.toolbox.register("attr_rsi_lo", random.randint, *bounds['RSI_LO'])
        self.toolbox.register("attr_sl", random.uniform, *bounds['SL'])
        self.toolbox.register("attr_tp", random.uniform, *bounds['TP'])
        
        # Structure initializer
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                            (self.toolbox.attr_sma_f, self.toolbox.attr_sma_s,
                             self.toolbox.attr_rsi_p, self.toolbox.attr_rsi_up,
                             self.toolbox.attr_rsi_lo, self.toolbox.attr_sl,
                             self.toolbox.attr_tp), n=1)
                             
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        # Operators
        self.toolbox.register("evaluate", eval_genome, data=self.data)
        self.toolbox.register("mate", tools.cxTwoPoint)
        
        # Custom mutation to handle Int and Float correctly
        self.toolbox.register("mutate", self._custom_mutation)
        self.toolbox.register("select", tools.selNSGA2)
        
    def _custom_mutation(self, individual, indpb=0.2):
        """Custom mutation handling mix of int and float."""
        # Indices of Int genes: 0, 1, 2, 3, 4
        # Indices of Float genes: 5, 6
        
        for i in range(len(individual)):
            if random.random() < indpb:
                if i < 5: # Integer genes
                    individual[i] = int(individual[i] + random.randint(-5, 5))
                    # Basic boundary checks (simplified)
                    if individual[i] < 5: individual[i] = 5
                else: # Float genes
                    individual[i] += random.gauss(0, 0.02)
                    if individual[i] < 0.01: individual[i] = 0.01
                    
        return individual,

    def run_evolution(self, population_size=Config.GA_POPULATION, generations=Config.GA_GENERATIONS, verbose=True):
        """Run the evolution loop."""
        
        # Create population
        pop = self.toolbox.population(n=population_size)
        
        # Stats
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)
        
        # Algorithms
        # Use simple EA or mu+lambda
        pop, logbook = algorithms.eaSimple(pop, self.toolbox, 
                                         cxpb=Config.GA_CXPB, 
                                         mutpb=Config.GA_MUTPB, 
                                         ngen=generations, 
                                         stats=stats, 
                                         verbose=verbose)
                                         
        return pop, logbook