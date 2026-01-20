# groupe-JVX/main.py
import argparse
import sys
from src.config import Config
from src.data_manager import DataManager
from src.ga_core import GAEcosystem
from src.walk_forward import WalkForwardAnalyzer
from src.strategy_genes import decode_chromosome
# Import de l'alias correct
from src.backtest_runner import run_simple_backtest 

def setup_argparse():
    parser = argparse.ArgumentParser(description='GA Trading System')
    parser.add_argument('--mode', type=str, choices=['test', 'simple', 'wfa', 'all'], 
                        default='simple', help='Execution mode')
    return parser.parse_args()

def test_data_download():
    print("\n" + "="*70)
    print("TESTING DATA DOWNLOAD")
    print("="*70)
    dm = DataManager()
    data = dm.get_full_data()
    if not data.empty:
        print("\nData downloaded successfully!")
        print(f"Rows: {len(data)}")
    else:
        print("Error: No data found.")

def run_simple_ga(dm):
    print("\n" + "="*70)
    print("RUNNING SIMPLE GENETIC ALGORITHM")
    print("="*70)
    
    full_data = dm.get_full_data()
    split_idx = int(len(full_data) * Config.TRAIN_RATIO)
    train_data = full_data.iloc[:split_idx]
    test_data = full_data.iloc[split_idx:]
    
    print(f"Train: {len(train_data)} | Test: {len(test_data)}")
    
    ga = GAEcosystem(train_data)
    pop, log = ga.run_evolution(verbose=True)
    
    best_ind = max(pop, key=lambda ind: ind.fitness.values[0])
    best_params = decode_chromosome(best_ind)
    
    print("\nBEST PARAMETERS:", best_params)
    print(f"In-Sample Fitness: {best_ind.fitness.values}")
    
    print("\n" + "="*70)
    print("OUT-OF-SAMPLE TESTING")
    print("="*70)
    # CORRECTION : On passe d'abord DATA puis PARAMS (ou on utilise le nommage explicite)
    run_simple_backtest(test_data, best_params, verbose=True)

def run_walk_forward(dm):
    wfa = WalkForwardAnalyzer(dm)
    wfa.run_analysis()

def main():
    args = setup_argparse()
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
            
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()