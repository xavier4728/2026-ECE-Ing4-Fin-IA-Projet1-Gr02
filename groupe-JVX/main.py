"""
Main entry point for the Genetic Algorithm Trading System.
"""
import argparse
import sys
from pathlib import Path
from src.config import Config
from src.data_manager import DataManager
from src.walk_forward import WalkForwardAnalysis
from src.ga_core import run_genetic_algorithm, get_best_individual
from src.strategy_genes import decode_chromosome
from src.backtest_runner import run_simple_backtest


def test_data_download():
    """
    Test data download functionality.
    """
    print("\n" + "="*70)
    print("TESTING DATA DOWNLOAD")
    print("="*70)
    
    dm = DataManager(ticker=Config.TICKER, interval=Config.INTERVAL)
    data = dm.get_full_data()
    
    print(f"\nData downloaded successfully!")
    print(f"Ticker: {Config.TICKER}")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
    print(f"Total bars: {len(data)}")
    print(f"\nFirst 5 rows:")
    print(data.head())
    print(f"\nLast 5 rows:")
    print(data.tail())
    
    return dm


def run_simple_ga(dm: DataManager):
    """
    Run a simple GA optimization on the full dataset.
    
    Args:
        dm: DataManager instance
    """
    print("\n" + "="*70)
    print("RUNNING SIMPLE GENETIC ALGORITHM")
    print("="*70)
    
    # Get data
    data = dm.get_full_data()
    
    # Split into train/test
    split_idx = int(len(data) * Config.TRAIN_RATIO)
    train_data = data.iloc[:split_idx]
    test_data = data.iloc[split_idx:]
    
    print(f"\nTrain data: {len(train_data)} bars ({train_data.index[0]} to {train_data.index[-1]})")
    print(f"Test data: {len(test_data)} bars ({test_data.index[0]} to {test_data.index[-1]})")
    
    # Run GA on training data
    print("\nOptimizing on training data...")
    population, toolbox, hof = run_genetic_algorithm(
        train_data,
        population_size=Config.GA_POPULATION,
        generations=Config.GA_GENERATIONS,
        verbose=True
    )
    
    # Get best individual
    if len(hof) > 0:
        best_individual = hof[0]
    else:
        best_individual = get_best_individual(population, prefer_profit=True)
    
    best_params = decode_chromosome(best_individual)
    
    print("\n" + "="*70)
    print("BEST PARAMETERS FOUND")
    print("="*70)
    for key, val in best_params.items():
        print(f"{key}: {val}")
    print(f"In-Sample Fitness: {best_individual.fitness.values}")
    
    # Test on out-of-sample data
    print("\n" + "="*70)
    print("OUT-OF-SAMPLE TESTING")
    print("="*70)
    
    oos_results = run_simple_backtest(best_params, test_data, verbose=True)
    
    return best_params, oos_results


def run_walk_forward(dm: DataManager):
    """
    Run walk-forward analysis.
    
    Args:
        dm: DataManager instance
    """
    print("\n" + "="*70)
    print("STARTING WALK-FORWARD ANALYSIS")
    print("="*70)
    
    wfa = WalkForwardAnalysis(
        dm,
        train_months=Config.WFA_TRAIN_MONTHS,
        test_months=Config.WFA_TEST_MONTHS,
        step_months=Config.WFA_STEP_MONTHS
    )
    
    results = wfa.run_analysis(
        start_date=Config.START_DATE,
        end_date=Config.END_DATE,
        ga_generations=Config.GA_GENERATIONS,
        ga_population=Config.GA_POPULATION,
        verbose=True
    )
    
    # Print summary
    print("\n" + "="*70)
    print("WALK-FORWARD ANALYSIS SUMMARY")
    print("="*70)
    print(f"Total Windows: {results['total_windows']}")
    print(f"\nAggregate Stats:")
    for key, val in results['aggregate_stats'].items():
        print(f"  {key}: {val}")
    print(f"\nBuy & Hold Benchmark:")
    for key, val in results['buy_hold_benchmark'].items():
        print(f"  {key}: {val}")
    
    return results


def main():
    """
    Main function with CLI argument parsing.
    """
    parser = argparse.ArgumentParser(
        description='Genetic Algorithm Trading System'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['test', 'simple', 'wfa', 'all'],
        default='all',
        help='Execution mode: test (data only), simple (single GA), wfa (walk-forward), all (complete pipeline)'
    )
    
    parser.add_argument(
        '--ticker',
        type=str,
        default=Config.TICKER,
        help=f'Trading symbol (default: {Config.TICKER})'
    )
    
    parser.add_argument(
        '--generations',
        type=int,
        default=Config.GA_GENERATIONS,
        help=f'Number of GA generations (default: {Config.GA_GENERATIONS})'
    )
    
    parser.add_argument(
        '--population',
        type=int,
        default=Config.GA_POPULATION,
        help=f'GA population size (default: {Config.GA_POPULATION})'
    )
    
    args = parser.parse_args()
    
    # Update config with CLI arguments
    Config.TICKER = args.ticker
    Config.GA_GENERATIONS = args.generations
    Config.GA_POPULATION = args.population
    
    # Create directories
    Path(Config.DATA_DIR).mkdir(exist_ok=True)
    Path(Config.LOGS_DIR).mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("GENETIC ALGORITHM TRADING SYSTEM")
    print("="*70)
    print(f"Ticker: {Config.TICKER}")
    print(f"GA Population: {Config.GA_POPULATION}")
    print(f"GA Generations: {Config.GA_GENERATIONS}")
    print(f"Mode: {args.mode}")
    print("="*70)
    
    try:
        # Initialize data manager
        dm = DataManager(ticker=Config.TICKER)
        
        if args.mode in ['test', 'all']:
            test_data_download()
        
        if args.mode in ['simple', 'all']:
            run_simple_ga(dm)
        
        if args.mode in ['wfa', 'all']:
            run_walk_forward(dm)
        
        print("\n" + "="*70)
        print("EXECUTION COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()