"""
Main entry point for the Genetic Algorithm Trading System.
"""
import argparse
import sys
from src.config import Config
from src.data_manager import DataManager
from src.ga_core import GAEcosystem
from src.walk_forward import WalkForwardAnalyzer
from src.strategy_genes import decode_chromosome

def setup_argparse():
    parser = argparse.ArgumentParser(description='GA Trading System')
    parser.add_argument('--mode', type=str, choices=['test', 'simple', 'wfa', 'all'], 
                        default='simple', help='Execution mode')
    return parser.parse_args()

def test_data_download():
    """Test only the data connection."""
    print("\n" + "="*70)
    print("TESTING DATA DOWNLOAD")
    print("="*70)
    dm = DataManager()
    data = dm.get_full_data()
    
    if not data.empty:
        print("\nData downloaded successfully!")
        print(f"Ticker: {Config.TICKER}")
        print(f"Date range: {data.index[0]} to {data.index[-1]}")
        print(f"Total bars: {len(data)}")
        print("\nFirst 5 rows:")
        print(data.head())
        print("\nLast 5 rows:")
        print(data.tail())
    else:
        print("Error: No data found.")

def run_simple_ga(dm):
    """Run a single optimization on the full training dataset."""
    print("\n" + "="*70)
    print("RUNNING SIMPLE GENETIC ALGORITHM")
    print("="*70)
    
    # Get Data
    # Pour le mode simple, on prend juste une tranche arbitraire (ex: 2020-2022) pour entraîner
    # Dans un vrai cas, on utiliserait le WFA, mais le mode simple sert de démo.
    full_data = dm.get_full_data()
    split_idx = int(len(full_data) * Config.TRAIN_RATIO)
    train_data = full_data.iloc[:split_idx]
    test_data = full_data.iloc[split_idx:]
    
    print(f"\nTrain data: {len(train_data)} bars ({train_data.index[0].date()} to {train_data.index[-1].date()})")
    print(f"Test data: {len(test_data)} bars ({test_data.index[0].date()} to {test_data.index[-1].date()})")
    
    print("\nOptimizing on training data...")
    print(f"Starting Genetic Algorithm (Pop: {Config.GA_POPULATION}, Gens: {Config.GA_GENERATIONS})")
    
    # --- NOUVELLE UTILISATION DE LA CLASSE GAEcosystem ---
    ga = GAEcosystem(train_data)
    pop, log = ga.run_evolution(verbose=True)
    
    print("\nEvolution completed!")
    
    # Get best individual
    best_ind = max(pop, key=lambda ind: ind.fitness.values[0])
    best_params = decode_chromosome(best_ind)
    
    print("\n" + "="*70)
    print("BEST PARAMETERS FOUND")
    print("="*70)
    for k, v in best_params.items():
        print(f"{k}: {v}")
    print(f"In-Sample Fitness: {best_ind.fitness.values}")
    
    # Run backtest on Test data with best params
    from src.backtest_runner import run_simple_backtest
    
    print("\n" + "="*70)
    print("OUT-OF-SAMPLE TESTING")
    print("="*70)
    run_simple_backtest(best_params, test_data, verbose=True)

def run_walk_forward(dm):
    """Run the Walk-Forward Analysis."""
    # --- NOUVELLE UTILISATION DE LA CLASSE WalkForwardAnalyzer ---
    wfa = WalkForwardAnalyzer(dm)
    wfa.run_analysis()

def main():
    args = setup_argparse()
    
    print("\n" + "="*70)
    print("GENETIC ALGORITHM TRADING SYSTEM")
    print("="*70)
    print(f"Ticker: {Config.TICKER}")
    print(f"Mode: {args.mode}")
    print("="*70)
    
    dm = DataManager()
    
    try:
        if args.mode == 'test':
            test_data_download()
        elif args.mode == 'simple':
            run_simple_ga(dm)
        elif args.mode == 'wfa':
            run_walk_forward(dm)
        elif args.mode == 'all':
            test_data_download()
            run_simple_ga(dm)
            run_walk_forward(dm)
            
        print("\n" + "="*70)
        print("EXECUTION COMPLETED SUCCESSFULLY")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Protection Windows Multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    main()