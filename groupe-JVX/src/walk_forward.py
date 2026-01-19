"""
Walk-Forward Analysis implementation for robust validation.
"""
import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.config import Config
from src.data_manager import DataManager
from src.ga_core import run_genetic_algorithm, get_best_individual
from src.strategy_genes import decode_chromosome
from src.backtest_runner import run_simple_backtest


class WalkForwardAnalysis:
    """
    Implements Walk-Forward Analysis to validate strategy robustness.
    """
    
    def __init__(self,
                 data_manager: DataManager,
                 train_months: int = Config.WFA_TRAIN_MONTHS,
                 test_months: int = Config.WFA_TEST_MONTHS,
                 step_months: int = Config.WFA_STEP_MONTHS):
        """
        Initialize Walk-Forward Analysis.
        
        Args:
            data_manager: DataManager instance
            train_months: Training window size in months
            test_months: Test window size in months
            step_months: Step size for sliding window in months
        """
        self.data_manager = data_manager
        self.train_months = train_months
        self.test_months = test_months
        self.step_months = step_months
        self.results: List[Dict] = []
        
    def generate_windows(self, start_date: str, end_date: str) -> List[Tuple[str, str, str, str]]:
        """
        Generate train/test windows for walk-forward analysis.
        
        Args:
            start_date: Overall start date
            end_date: Overall end date
            
        Returns:
            List[Tuple]: List of (train_start, train_end, test_start, test_end) tuples
        """
        windows = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while True:
            # Calculate train window
            train_start = current_date
            train_end = train_start + relativedelta(months=self.train_months)
            
            # Calculate test window
            test_start = train_end
            test_end = test_start + relativedelta(months=self.test_months)
            
            # Check if we've exceeded the end date
            if test_end > end:
                break
            
            windows.append((
                train_start.strftime('%Y-%m-%d'),
                train_end.strftime('%Y-%m-%d'),
                test_start.strftime('%Y-%m-%d'),
                test_end.strftime('%Y-%m-%d')
            ))
            
            # Move to next window
            current_date = current_date + relativedelta(months=self.step_months)
        
        return windows
    
    def run_analysis(self,
                    start_date: str,
                    end_date: str,
                    ga_generations: int = Config.GA_GENERATIONS,
                    ga_population: int = Config.GA_POPULATION,
                    verbose: bool = True) -> Dict:
        """
        Run complete walk-forward analysis.
        
        Args:
            start_date: Analysis start date
            end_date: Analysis end date
            ga_generations: Number of GA generations
            ga_population: GA population size
            verbose: Print progress
            
        Returns:
            Dict: Complete analysis results
        """
        windows = self.generate_windows(start_date, end_date)
        
        if verbose:
            print("\n" + "="*70)
            print("WALK-FORWARD ANALYSIS")
            print("="*70)
            print(f"Total Windows: {len(windows)}")
            print(f"Train: {self.train_months} months | Test: {self.test_months} months")
            print(f"Step: {self.step_months} months")
            print("="*70 + "\n")
        
        self.results = []
        oos_profits = []
        
        for i, (train_start, train_end, test_start, test_end) in enumerate(windows):
            if verbose:
                print(f"\n{'='*70}")
                print(f"Window {i+1}/{len(windows)}")
                print(f"Train: {train_start} to {train_end}")
                print(f"Test:  {test_start} to {test_end}")
                print(f"{'='*70}")
            
            # Get training data
            train_data = self.data_manager.get_data_slice(train_start, train_end)
            
            if verbose:
                print(f"\nTraining data: {len(train_data)} bars")
                print("Running Genetic Algorithm on training data...")
            
            # Run GA on training data
            population, toolbox, hof = run_genetic_algorithm(
                train_data,
                population_size=ga_population,
                generations=ga_generations,
                verbose=verbose
            )
            
            # Get best individual from Pareto front
            if len(hof) > 0:
                best_individual = hof[0]  # First from Pareto front
            else:
                best_individual = get_best_individual(population, prefer_profit=True)
            
            best_params = decode_chromosome(best_individual)
            
            if verbose:
                print(f"\nBest parameters found:")
                for key, val in best_params.items():
                    print(f"  {key}: {val}")
            
            # Test on out-of-sample data
            test_data = self.data_manager.get_data_slice(test_start, test_end)
            
            if verbose:
                print(f"\nTesting on out-of-sample data: {len(test_data)} bars")
            
            oos_results = run_simple_backtest(
                best_params,
                test_data,
                verbose=verbose
            )
            
            # Store results
            window_result = {
                'window': i + 1,
                'train_start': train_start,
                'train_end': train_end,
                'test_start': test_start,
                'test_end': test_end,
                'best_params': best_params,
                'in_sample_fitness': best_individual.fitness.values,
                'oos_profit_pct': oos_results.get('profit_pct', -100),
                'oos_trades': oos_results.get('total_trades', 0),
                'oos_win_rate': oos_results.get('win_rate', 0),
                'oos_max_drawdown': oos_results.get('max_drawdown', 0),
            }
            
            self.results.append(window_result)
            oos_profits.append(oos_results.get('profit_pct', -100))
        
        # Calculate aggregate statistics
        aggregate_stats = self._calculate_aggregate_stats(oos_profits, verbose)
        
        # Calculate buy and hold benchmark
        buy_hold_stats = self._calculate_buy_hold(start_date, end_date, verbose)
        
        return {
            'windows': self.results,
            'aggregate_stats': aggregate_stats,
            'buy_hold_benchmark': buy_hold_stats,
            'total_windows': len(windows),
        }
    
    def _calculate_aggregate_stats(self, oos_profits: List[float], verbose: bool = True) -> Dict:
        """
        Calculate aggregate out-of-sample statistics.
        
        Args:
            oos_profits: List of OOS profit percentages
            verbose: Print results
            
        Returns:
            Dict: Aggregate statistics
        """
        import numpy as np
        
        stats = {
            'mean_profit': np.mean(oos_profits),
            'median_profit': np.median(oos_profits),
            'std_profit': np.std(oos_profits),
            'min_profit': np.min(oos_profits),
            'max_profit': np.max(oos_profits),
            'positive_windows': sum(1 for p in oos_profits if p > 0),
            'negative_windows': sum(1 for p in oos_profits if p < 0),
            'win_rate': (sum(1 for p in oos_profits if p > 0) / len(oos_profits)) * 100,
        }
        
        if verbose:
            print("\n" + "="*70)
            print("AGGREGATE OUT-OF-SAMPLE RESULTS")
            print("="*70)
            print(f"Mean Profit: {stats['mean_profit']:.2f}%")
            print(f"Median Profit: {stats['median_profit']:.2f}%")
            print(f"Std Dev: {stats['std_profit']:.2f}%")
            print(f"Min Profit: {stats['min_profit']:.2f}%")
            print(f"Max Profit: {stats['max_profit']:.2f}%")
            print(f"Positive Windows: {stats['positive_windows']}/{len(oos_profits)}")
            print(f"Window Win Rate: {stats['win_rate']:.2f}%")
            print("="*70 + "\n")
        
        return stats
    
    def _calculate_buy_hold(self, start_date: str, end_date: str, verbose: bool = True) -> Dict:
        """
        Calculate buy and hold benchmark performance.
        
        Args:
            start_date: Start date
            end_date: End date
            verbose: Print results
            
        Returns:
            Dict: Buy and hold statistics
        """
        data = self.data_manager.get_data_slice(start_date, end_date)
        
        initial_price = data['Close'].iloc[0]
        final_price = data['Close'].iloc[-1]
        profit_pct = ((final_price - initial_price) / initial_price) * 100
        
        stats = {
            'initial_price': initial_price,
            'final_price': final_price,
            'profit_pct': profit_pct,
        }
        
        if verbose:
            print("="*70)
            print("BUY & HOLD BENCHMARK")
            print("="*70)
            print(f"Initial Price: ${initial_price:,.2f}")
            print(f"Final Price: ${final_price:,.2f}")
            print(f"Buy & Hold Profit: {profit_pct:.2f}%")
            print("="*70 + "\n")
        
        return stats