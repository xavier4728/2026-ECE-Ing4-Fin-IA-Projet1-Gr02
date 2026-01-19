"""
Backtrader strategy implementation with genetic algorithm parameters.
"""
import backtrader as bt
from typing import Dict


class GeneticStrategy(bt.Strategy):
    """
    Trading strategy with parameters optimized by genetic algorithm.
    Uses SMA crossover and RSI for entry/exit signals.
    """
    
    params = (
        ('SMA_F', 20),      # Fast SMA period
        ('SMA_S', 100),     # Slow SMA period
        ('RSI_P', 14),      # RSI period
        ('RSI_UP', 70),     # RSI overbought threshold
        ('RSI_LO', 30),     # RSI oversold threshold
        ('SL', 0.05),       # Stop Loss percentage
        ('TP', 0.10),       # Take Profit percentage
    )
    
    def __init__(self):
        """
        Initialize strategy indicators and state.
        """
        # Validate parameters
        if self.params.SMA_F >= self.params.SMA_S:
            self.valid_params = False
        else:
            self.valid_params = True
        
        # Initialize indicators
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.SMA_F
        )
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.SMA_S
        )
        self.rsi = bt.indicators.RSI(
            self.data.close, period=self.params.RSI_P
        )
        
        # Track order status
        self.order = None
        self.buy_price = None
        
    def notify_order(self, order):
        """
        Handle order notifications.
        
        Args:
            order: Order object from Backtrader
        """
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
            self.order = None
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
    
    def next(self):
        """
        Execute strategy logic on each bar.
        """
        # Skip if parameters are invalid
        if not self.valid_params:
            return
        
        # Skip if we have a pending order
        if self.order:
            return
        
        # Entry Logic (Long only)
        if not self.position:
            # Conditions:
            # 1. Close > Fast SMA
            # 2. Fast SMA > Slow SMA
            # 3. RSI < Oversold threshold
            if (self.data.close[0] > self.sma_fast[0] and
                self.sma_fast[0] > self.sma_slow[0] and
                self.rsi[0] < self.params.RSI_LO):
                
                # Calculate stop loss and take profit prices
                current_price = self.data.close[0]
                stop_price = current_price * (1 - self.params.SL)
                limit_price = current_price * (1 + self.params.TP)
                
                # Use buy bracket for automatic SL/TP
                self.order = self.buy_bracket(
                    size=None,  # Use all available cash
                    stopprice=stop_price,
                    limitprice=limit_price
                )
        
        # Exit Logic
        else:
            # Exit if:
            # 1. RSI > Overbought threshold OR
            # 2. Close < Slow SMA
            if (self.rsi[0] > self.params.RSI_UP or
                self.data.close[0] < self.sma_slow[0]):
                
                self.order = self.close()


def decode_chromosome(chromosome: list) -> Dict[str, float]:
    """
    Decode a chromosome (list of genes) into strategy parameters.
    
    Args:
        chromosome: List of 7 genes [SMA_F, SMA_S, RSI_P, RSI_UP, RSI_LO, SL, TP]
        
    Returns:
        Dict[str, float]: Parameter dictionary for the strategy
    """
    return {
        'SMA_F': int(chromosome[0]),
        'SMA_S': int(chromosome[1]),
        'RSI_P': int(chromosome[2]),
        'RSI_UP': int(chromosome[3]),
        'RSI_LO': int(chromosome[4]),
        'SL': float(chromosome[5]),
        'TP': float(chromosome[6]),
    }


def encode_params(params: Dict[str, float]) -> list:
    """
    Encode strategy parameters into a chromosome.
    
    Args:
        params: Parameter dictionary
        
    Returns:
        list: Chromosome as list of genes
    """
    return [
        params['SMA_F'],
        params['SMA_S'],
        params['RSI_P'],
        params['RSI_UP'],
        params['RSI_LO'],
        params['SL'],
        params['TP'],
    ]