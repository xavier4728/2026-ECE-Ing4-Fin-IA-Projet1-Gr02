"""
Walk-Forward Analysis Module (CORRIGÉ - Fix du bug de trading).
"""
import pandas as pd
from dateutil.relativedelta import relativedelta
from src.ga_core import GAEcosystem
from src.backtest_runner import run_simple_backtest
from src.strategy_genes import decode_chromosome
from src.config import Config

class WalkForwardAnalyzer:
    """
    Orchestrates the Walk-Forward Analysis (WFA) process.
    Train on Window N -> Test on Window N+1 -> Slide.
    """
    
    def __init__(self, data_manager):
        self.dm = data_manager
        
    def run_analysis(self):
        print("\n" + "="*70)
        print("STARTING WALK-FORWARD ANALYSIS (WITH WARM-UP)")
        print("="*70)
        
        # Get full dataset
        full_data = self.dm.get_full_data()
        if full_data.empty:
            print("Error: No data available for WFA.")
            return []
            
        start_date = full_data.index[0]
        end_date = full_data.index[-1]
        
        current_train_start = start_date
        
        wfa_results = []
        window_count = 1
        
        # Boucle Principale
        while True:
            # Define periods
            train_end = current_train_start + relativedelta(months=Config.WFA_TRAIN_MONTHS)
            test_start = train_end  # ✅ Le test commence immédiatement après le train
            test_end = test_start + relativedelta(months=Config.WFA_TEST_MONTHS)
            
            # Stop if we exceed data
            if test_end > end_date:
                break
                
            print(f"\n--- Window {window_count} ---")
            print(f"Train: {current_train_start.date()} -> {train_end.date()}")
            print(f"Test:  {test_start.date()} -> {test_end.date()}")
            
            # ✅ CORRECTION MAJEURE : Warm-up séparé
            # On calcule le SMA_S max possible (200 par défaut, mais ici limité à 60)
            max_indicator_period = 60  # Config.GENE_BOUNDS['SMA_S'][1]
            
            # On prend N jours de données AVANT test_start pour chauffer les indicateurs
            # (en jours de bourse, donc on prend large : 60 jours = ~3 mois calendaires)
            warmup_buffer_days = max_indicator_period + 10  # Marge de sécurité
            
            # On cherche la date de début du warm-up en reculant dans full_data
            test_data_index = full_data.index.get_loc(test_start, method='nearest')
            warmup_start_index = max(0, test_data_index - warmup_buffer_days)
            warmup_start = full_data.index[warmup_start_index]
            
            print(f"Warm-up: {warmup_start.date()} -> {test_start.date()} ({warmup_buffer_days} bars)")
            
            # 1. Get Data Slices
            train_data = self.dm.get_data_slice(
                str(current_train_start.date()), 
                str(train_end.date())
            )
            
            # ✅ Test data INCLUT le warm-up (depuis warmup_start)
            test_data_with_warmup = self.dm.get_data_slice(
                str(warmup_start.date()), 
                str(test_end.date())
            )
            
            if len(train_data) < 50:
                print("Skipping window: Not enough training data.")
                current_train_start += relativedelta(months=Config.WFA_STEP_MONTHS)
                window_count += 1
                continue
                
            if len(test_data_with_warmup) < warmup_buffer_days + 10:
                print("Skipping window: Not enough test data (including warm-up).")
                current_train_start += relativedelta(months=Config.WFA_STEP_MONTHS)
                window_count += 1
                continue

            # 2. Optimization (Train)
            print("  > Optimizing...")
            ga = GAEcosystem(train_data)
            pop, log = ga.run_evolution(population_size=30, generations=5, verbose=False)
            
            # Select Best Individual (Max Profit)
            best_ind = max(pop, key=lambda ind: ind.fitness.values[0])
            best_params = decode_chromosome(best_ind)
            
            print(f"  > Best Params: SMA_F={best_params['SMA_F']}, SMA_S={best_params['SMA_S']}, RSI_LO={best_params['RSI_LO']}")
            
            # 3. Validation (Test)
            print("  > Testing on unseen data (with warm-up)...")
            
            # ✅ CORRECTION : On passe test_start (pas train_end) comme date de début de trading
            result = run_simple_backtest(
                best_params, 
                test_data_with_warmup, 
                verbose=False,
                trading_start_date=test_start.date()  # ✅ FIX : Date de début du test réel
            )
            
            window_result = {
                'window': window_count,
                'train_period': f"{current_train_start.date()} to {train_end.date()}",
                'test_period': f"{test_start.date()} to {test_end.date()}",
                'profit_pct': result['profit_pct'],
                'drawdown': result['max_drawdown'],
                'trades': result['total_trades'],
                'win_rate': result.get('win_rate', 0)
            }
            wfa_results.append(window_result)
            
            print(f"  > Result: Profit {result['profit_pct']:.2f}% | Trades: {result['total_trades']} | WR: {result.get('win_rate', 0):.1f}%")
            
            # Slide Window
            current_train_start += relativedelta(months=Config.WFA_STEP_MONTHS)
            window_count += 1
            
        self._print_summary(wfa_results)
        return wfa_results

    def _print_summary(self, results):
        if not results:
            print("No results generated.")
            return

        print("\n" + "="*70)
        print("WFA FINAL SUMMARY")
        print("="*70)
        
        total_profit = 0
        total_trades = 0
        wins = 0
        
        print(f"{'Window':<8} | {'Test Period':<25} | {'Profit %':<10} | {'Trades':<8} | {'WR %':<8}")
        print("-" * 75)
        
        for r in results:
            print(f"{r['window']:<8} | {r['test_period']:<25} | {r['profit_pct']:>9.2f}% | {r['trades']:>8} | {r['win_rate']:>7.1f}%")
            total_profit += r['profit_pct']
            total_trades += r['trades']
            if r['profit_pct'] > 0: wins += 1
            
        print("-" * 75)
        avg_profit = total_profit / len(results) if results else 0
        win_rate = (wins / len(results)) * 100 if results else 0
        
        print(f"Average Profit per Window: {avg_profit:.2f}%")
        print(f"Total Cumulative Profit (Simple Sum): {total_profit:.2f}%")
        print(f"Window Win Rate: {win_rate:.2f}%")
        print(f"Total Trades Across All Windows: {total_trades}")
        print("="*70)