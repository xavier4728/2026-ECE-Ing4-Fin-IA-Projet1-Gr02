"""
Genetic Algorithm core implementation using DEAP.
"""
import random
import numpy as np
import pandas as pd
from typing import Tuple, List
from deap import base, creator, tools, algorithms
from src.config import Config
from src.strategy_genes import decode_chromosome
from src.backtest_runner import run_backtest


# Global variable for data (needed for multiprocessing on Windows)
_GLOBAL_DATA = None


def set_global_data(data: pd.DataFrame):
    """
    Set global data for evaluation function.
    
    Args:
        data: Market data DataFrame
    """
    global _GLOBAL_DATA
    _GLOBAL_DATA = data


def evaluate_individual(individual: List[float]) -> Tuple[float, float]:
    """
    Evaluate a single individual (chromosome).
    This function must be at module level for Windows multiprocessing.
    
    Args:
        individual: List of genes representing strategy parameters
        
    Returns:
        Tuple[float, float]: (profit, -drawdown) for multi-objective optimization
    """
    global _GLOBAL_DATA
    
    if _GLOBAL_DATA is None:
        return (float('-inf'), float('-inf'))
    
    # Decode chromosome to parameters
    params = decode_chromosome(individual)
    
    # Run backtest
    profit_pct, max_drawdown_pct = run_backtest(params, _GLOBAL_DATA)
    
    # Return fitness (maximize profit, minimize drawdown)
    # Note: DEAP maximizes both objectives, so we negate drawdown
    return (profit_pct, -max_drawdown_pct)


def create_individual() -> List[float]:
    """
    Create a random individual respecting gene bounds.
    
    Returns:
        List[float]: Random chromosome
    """
    bounds = Config.GENE_BOUNDS
    
    individual = [
        random.randint(bounds['SMA_F'][0], bounds['SMA_F'][1]),  # SMA_F
        random.randint(bounds['SMA_S'][0], bounds['SMA_S'][1]),  # SMA_S
        random.randint(bounds['RSI_P'][0], bounds['RSI_P'][1]),  # RSI_P
        random.randint(bounds['RSI_UP'][0], bounds['RSI_UP'][1]),  # RSI_UP
        random.randint(bounds['RSI_LO'][0], bounds['RSI_LO'][1]),  # RSI_LO
        random.uniform(bounds['SL'][0], bounds['SL'][1]),  # SL
        random.uniform(bounds['TP'][0], bounds['TP'][1]),  # TP
    ]
    
    return individual


def mutate_individual(individual: List[float], indpb: float = 0.2) -> Tuple[List[float]]:
    """
    Mutate an individual with boundary checking.
    
    Args:
        individual: Chromosome to mutate
        indpb: Probability of mutating each gene
        
    Returns:
        Tuple containing the mutated individual
    """
    bounds = Config.GENE_BOUNDS
    gene_names = ['SMA_F', 'SMA_S', 'RSI_P', 'RSI_UP', 'RSI_LO', 'SL', 'TP']
    
    for i in range(len(individual)):
        if random.random() < indpb:
            gene_name = gene_names[i]
            min_val, max_val = bounds[gene_name]
            
            if i < 5:  # Integer genes
                delta = random.randint(-5, 5)
                individual[i] = int(np.clip(individual[i] + delta, min_val, max_val))
            else:  # Float genes (SL, TP)
                delta = random.uniform(-0.01, 0.01)
                individual[i] = float(np.clip(individual[i] + delta, min_val, max_val))
    
    return (individual,)


def setup_deap_toolbox(data: pd.DataFrame) -> base.Toolbox:
    """
    Setup DEAP toolbox with genetic operators.
    
    Args:
        data: Market data for evaluation
        
    Returns:
        base.Toolbox: Configured DEAP toolbox
    """
    # Set global data for evaluation
    set_global_data(data)
    
    # Create fitness and individual classes
    # Fitness: maximize profit (weight=1.0), minimize drawdown (weight=-1.0)
    if not hasattr(creator, "FitnessMulti"):
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
    
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMulti)
    
    # Create toolbox
    toolbox = base.Toolbox()
    
    # Register genetic operators
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate_individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_individual, indpb=0.2)
    toolbox.register("select", tools.selNSGA2)
    
    return toolbox


def run_genetic_algorithm(data: pd.DataFrame,
                         population_size: int = Config.GA_POPULATION,
                         generations: int = Config.GA_GENERATIONS,
                         cxpb: float = Config.GA_CXPB,
                         mutpb: float = Config.GA_MUTPB,
                         verbose: bool = True) -> Tuple[List, base.Toolbox]:
    """
    Run the genetic algorithm optimization.
    
    Args:
        data: Market data for backtesting
        population_size: Number of individuals in population
        generations: Number of generations to evolve
        cxpb: Crossover probability
        mutpb: Mutation probability
        verbose: Print progress
        
    Returns:
        Tuple[List, base.Toolbox]: (final_population, toolbox)
    """
    # Setup toolbox
    toolbox = setup_deap_toolbox(data)
    
    # Create initial population
    population = toolbox.population(n=population_size)
    
    # Statistics
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    
    # Hall of fame to keep best individuals
    hof = tools.ParetoFront()
    
    if verbose:
        print(f"\nStarting Genetic Algorithm")
        print(f"Population: {population_size}, Generations: {generations}")
        print(f"Crossover: {cxpb}, Mutation: {mutpb}\n")
    
    # Run evolution
    population, logbook = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=cxpb,
        mutpb=mutpb,
        ngen=generations,
        stats=stats,
        halloffame=hof,
        verbose=verbose
    )
    
    if verbose:
        print(f"\nEvolution completed!")
        print(f"Pareto Front size: {len(hof)}")
        
        # Show best individuals
        print("\nTop 3 individuals from Pareto Front:")
        for i, ind in enumerate(hof[:3]):
            params = decode_chromosome(ind)
            print(f"\n#{i+1} - Fitness: {ind.fitness.values}")
            print(f"  Parameters: {params}")
    
    return population, toolbox, hof


def get_best_individual(population: List, prefer_profit: bool = True) -> List[float]:
    """
    Get the best individual from population based on criteria.
    
    Args:
        population: List of individuals
        prefer_profit: If True, prefer high profit; if False, prefer low drawdown
        
    Returns:
        List[float]: Best individual chromosome
    """
    if prefer_profit:
        # Sort by profit (first objective)
        best = max(population, key=lambda ind: ind.fitness.values[0])
    else:
        # Sort by drawdown (second objective, already negated)
        best = max(population, key=lambda ind: ind.fitness.values[1])
    
    return best