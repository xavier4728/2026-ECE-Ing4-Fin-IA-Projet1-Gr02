"""
Backtest runner module using Backtrader engine.
"""
import backtrader as bt
import pandas as pd
import traceback
from typing import Tuple, Dict
from src.strategy_genes import GeneticStrategy
from src.config import Config


class PandasData(bt.feeds.PandasData):
    """
    Custom Pandas data feed for Backtrader.
    """
    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
        ('openinterest', None),
    )


def run_backtest(params: Dict[str, float], data_feed: pd.DataFrame) -> Tuple[float, float]:
    """
    Run a backtest with given strategy parameters and data.
    """
    try:
        # Validate data
        if data_feed.empty or len(data_feed) < 100:
            return (-100.0, 100.0)
        
        # Create Cerebro engine
        cerebro = bt.Cerebro()
        
        # Add strategy with parameters
        cerebro.addstrategy(GeneticStrategy, **params)
        
        # Add data feed
        data = PandasData(dataname=data_feed)
        cerebro.adddata(data)
        
        # Set initial cash
        cerebro.broker.setcash(Config.INITIAL_CASH)
        
        # Set commission
        cerebro.broker.setcommission(commission=Config.get_commission())
        
        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        
        # Run backtest
        initial_value = cerebro.broker.getvalue()
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        
        # Extract results
        strat = results[0]
        
        # Get trade analyzer
        trade_analysis = strat.analyzers.trades.get_analysis()
        
        # --- CORRECTION: Accès sécurisé via .get() ---
        # Si 'total' n'existe pas, on considère qu'il y a 0 trades
        total_trades = trade_analysis.get('total', {}).get('closed', 0)
        
        if total_trades == 0:
            # No trades executed
            return (-100.0, 100.0)
        
        # Calculate profit percentage
        profit_pct = ((final_value - initial_value) / initial_value) * 100.0
        
        # Get drawdown
        dd_analysis = strat.analyzers.drawdown.get_analysis()
        # Correction similaire pour le drawdown
        max_drawdown_pct = dd_analysis.get('max', {}).get('drawdown', 0.0)
        
        # Handle invalid values
        if pd.isna(profit_pct) or pd.isna(max_drawdown_pct):
            return (-100.0, 100.0)
        
        return (profit_pct, max_drawdown_pct)
        
    except ZeroDivisionError:
        return (float('-inf'), float('+inf'))
    
    except Exception:
        # En cas d'autre crash, on l'affiche mais on ne tue pas le programme
        # print("\n!!! BACKTEST CRASH !!!")
        # traceback.print_exc()
        return (float('-inf'), float('+inf'))


def run_simple_backtest(params: Dict[str, float], 
                       data_feed: pd.DataFrame,
                       initial_cash: float = Config.INITIAL_CASH,
                       verbose: bool = True) -> Dict:
    """
    Run a simple backtest and return detailed results.
    """
    try:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(GeneticStrategy, **params)
        
        data = PandasData(dataname=data_feed)
        cerebro.adddata(data)
        
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=Config.get_commission())
        
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        
        initial_value = cerebro.broker.getvalue()
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        
        strat = results[0]
        
        # Extract detailed metrics
        trade_analysis = strat.analyzers.trades.get_analysis()
        dd_analysis = strat.analyzers.drawdown.get_analysis()
        sharpe = strat.analyzers.sharpe.get_analysis()
        
        # --- CORRECTION: Accès sécurisé pour tous les champs ---
        total_trades = trade_analysis.get('total', {}).get('closed', 0)
        won_trades = trade_analysis.get('won', {}).get('total', 0)
        lost_trades = trade_analysis.get('lost', {}).get('total', 0)
        
        max_drawdown = dd_analysis.get('max', {}).get('drawdown', 0.0)
        sharpe_ratio = sharpe.get('sharperatio', 0.0)

        results_dict = {
            'initial_value': initial_value,
            'final_value': final_value,
            'profit': final_value - initial_value,
            'profit_pct': ((final_value - initial_value) / initial_value) * 100,
            'total_trades': total_trades,
            'won_trades': won_trades,
            'lost_trades': lost_trades,
            'win_rate': (won_trades / total_trades * 100) if total_trades > 0 else 0,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio if sharpe_ratio is not None else 0,
        }
        
        if verbose:
            print("\n" + "="*50)
            print("BACKTEST RESULTS")
            print("="*50)
            print(f"Initial Value: ${results_dict['initial_value']:,.2f}")
            print(f"Final Value: ${results_dict['final_value']:,.2f}")
            print(f"Profit: ${results_dict['profit']:,.2f} ({results_dict['profit_pct']:.2f}%)")
            print(f"Total Trades: {results_dict['total_trades']}")
            print(f"Won: {results_dict['won_trades']} | Lost: {results_dict['lost_trades']}")
            print(f"Win Rate: {results_dict['win_rate']:.2f}%")
            print(f"Max Drawdown: {results_dict['max_drawdown']:.2f}%")
            print(f"Sharpe Ratio: {results_dict['sharpe_ratio']:.4f}")
            print("="*50 + "\n")
        
        return results_dict
        
    except Exception:
        print("\n!!! BACKTEST CRASH (Simple Mode) !!!")
        traceback.print_exc()
        return {
            'error': 'Crash detected',
            'profit_pct': -100.0,
            'max_drawdown': 100.0,
        }