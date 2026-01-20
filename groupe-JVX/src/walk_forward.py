# groupe-JVX/src/walk_forward.py
import pandas as pd
from dateutil.relativedelta import relativedelta
from src.ga_core import GAEcosystem
from src.backtest_runner import run_simple_backtest
from src.strategy_genes import decode_chromosome
from src.config import Config

class WalkForwardAnalyzer:
    
    def __init__(self, data_manager):
        self.dm = data_manager
        
    def run_analysis(self):
        print("\n" + "="*70)
        print("STARTING WALK-FORWARD ANALYSIS (WITH WARM-UP)")
        print("="*70)
        
        full_data = self.dm.get_full_data()
        if full_data.empty:
            print("Error: No data available for WFA.")
            return []
            
        start_date = full_data.index[0]
        end_date = full_data.index[-1]
        
        current_train_start = start_date
        wfa_results = []
        window_count = 1
        
        while True:
            # Périodes
            train_end = current_train_start + relativedelta(months=Config.WFA_TRAIN_MONTHS)
            test_start = train_end
            test_end = test_start + relativedelta(months=Config.WFA_TEST_MONTHS)
            
            if test_end > end_date:
                break
                
            print(f"\n--- Window {window_count} ---")
            print(f"Train: {current_train_start.date()} -> {train_end.date()}")
            print(f"Test:  {test_start.date()} -> {test_end.date()}")
            
            # WARM-UP LOGIC
            max_indicator_period = 60
            warmup_buffer_days = max_indicator_period + 10
            
            try:
                test_data_index = full_data.index.get_loc(test_start, method='nearest')
                warmup_start_index = max(0, test_data_index - warmup_buffer_days)
                warmup_start = full_data.index[warmup_start_index]
            except:
                # Fallback si dates hors limites
                warmup_start = test_start
            
            # Data Slicing
            train_data = self.dm.get_data_slice(str(current_train_start.date()), str(train_end.date()))
            test_data_with_warmup = self.dm.get_data_slice(str(warmup_start.date()), str(test_end.date()))
            
            # Vérifications taille
            if len(train_data) < 50:
                print("Skipping window: Not enough training data.")
                current_train_start += relativedelta(months=Config.WFA_STEP_MONTHS)
                continue

            # 1. OPTIMISATION (Sur Train)
            print("  > Optimizing...")
            ga = GAEcosystem(train_data)
            # CORRECTION : Pas d'arguments pop/gen ici, tout est dans Config via ga_core
            pop, log = ga.run_evolution(verbose=False)
            
            best_ind = max(pop, key=lambda ind: ind.fitness.values[0])
            best_params = decode_chromosome(best_ind)
            
            print(f"  > Best Params: SMA_F={best_params['SMA_F']}, SMA_S={best_params['SMA_S']}, RSI_LO={best_params['RSI_LO']}")
            
            # 2. TEST (Sur Test avec Warmup)
            print("  > Testing on unseen data (with warm-up)...")
            
            # On lance le backtest en spécifiant QUAND commencer à trader
            result = run_simple_backtest(
                test_data_with_warmup, 
                best_params, 
                verbose=False,
                trading_start_date=test_start.date() # Le trading commence après le warm-up
            )
            
            # CORRECTION CLES RESULTATS (Backtesting.py output keys)
            profit = result['Return [%]']
            trades = result['# Trades']
            dd = result['Max. Drawdown [%]']
            win_rate = result['Win Rate [%]']
            
            # Gestion des NaN si 0 trades
            if pd.isna(win_rate): win_rate = 0.0

            window_result = {
                'window': window_count,
                'train_period': f"{current_train_start.date()} to {train_end.date()}",
                'test_period': f"{test_start.date()} to {test_end.date()}",
                'profit_pct': profit,
                'drawdown': dd,
                'trades': trades,
                'win_rate': win_rate
            }
            wfa_results.append(window_result)
            
            print(f"  > Result: Profit {profit:.2f}% | Trades: {trades} | WR: {win_rate:.1f}%")
            
            # Slide
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
        # Moyenne simple des profits (Attention: en réalité il faudrait composer les rendements)
        avg_profit = total_profit / len(results) if results else 0
        global_win_rate = (wins / len(results)) * 100 if results else 0
        
        print(f"Average Profit per Window: {avg_profit:.2f}%")
        print(f"Total Cumulative Profit: {total_profit:.2f}%")
        print(f"Windows with Profit: {wins}/{len(results)} ({global_win_rate:.1f}%)")
        print("="*70)