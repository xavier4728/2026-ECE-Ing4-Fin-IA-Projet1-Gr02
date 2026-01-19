"""
Genetic Algorithm Trading System - Source Package
"""

__version__ = "1.0.0"
__author__ = "Equipe JVX (Jean-François, Valentin, Xavier)"

from src.config import Config
from src.data_manager import DataManager
from src.strategy_genes import GeneticStrategy, decode_chromosome
from src.backtest_runner import run_backtest, run_simple_backtest
from src.ga_core import run_genetic_algorithm, get_best_individual
from src.walk_forward import WalkForwardAnalysis

__all__ = [
    'Config',
    'DataManager',
    'GeneticStrategy',
    'decode_chromosome',
    'run_backtest',
    'run_simple_backtest',
    'run_genetic_algorithm',
    'get_best_individual',
    'WalkForwardAnalysis',
]