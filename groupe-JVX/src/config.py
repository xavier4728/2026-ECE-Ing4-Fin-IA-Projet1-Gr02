"""
Central configuration module for the Genetic Algorithm Trading System.
"""
from typing import Dict, Any


class Config:
    """
    Centralized configuration for data, backtesting, and GA parameters.
    """
    
    # === Market Data ===
    TICKER: str = "BTC-USD"  # Can be changed to "SPY" for stocks
    INTERVAL: str = "1d"
    START_DATE: str = "2020-01-01"
    END_DATE: str = "2024-01-01"
    
    # === Data Split ===
    TRAIN_RATIO: float = 0.70
    TEST_RATIO: float = 0.30
    
    # === Backtesting ===
    INITIAL_CASH: float = 10_000.0
    COMMISSION_CRYPTO: float = 0.001
    COMMISSION_STOCK: float = 0.0001
    
    @classmethod
    def get_commission(cls) -> float:
        """
        Returns the appropriate commission based on asset type.
        
        Returns:
            float: Commission rate
        """
        if "BTC" in cls.TICKER or "ETH" in cls.TICKER:
            return cls.COMMISSION_CRYPTO
        return cls.COMMISSION_STOCK
    
    # === Genetic Algorithm ===
    GA_POPULATION: int = 50
    GA_GENERATIONS: int = 10
    GA_CXPB: float = 0.7  # Crossover probability
    GA_MUTPB: float = 0.2  # Mutation probability
    
    # === Walk-Forward Analysis ===
    WFA_TRAIN_MONTHS: int = 12
    WFA_TEST_MONTHS: int = 3
    WFA_STEP_MONTHS: int = 3
    
    # === Gene Bounds ===
    # [min, max] for each gene
    GENE_BOUNDS: Dict[str, tuple] = {
        'SMA_F': (5, 50),      # Fast SMA period
        'SMA_S': (50, 200),    # Slow SMA period
        'RSI_P': (5, 30),      # RSI period
        'RSI_UP': (60, 90),    # RSI overbought threshold
        'RSI_LO': (10, 40),    # RSI oversold threshold
        'SL': (0.01, 0.10),    # Stop Loss percentage
        'TP': (0.02, 0.20),    # Take Profit percentage
    }
    
    # === Paths ===
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"
    
    @classmethod
    def get_params_dict(cls) -> Dict[str, Any]:
        """
        Returns a dictionary of all configuration parameters.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        return {
            'ticker': cls.TICKER,
            'interval': cls.INTERVAL,
            'start_date': cls.START_DATE,
            'end_date': cls.END_DATE,
            'initial_cash': cls.INITIAL_CASH,
            'commission': cls.get_commission(),
            'ga_population': cls.GA_POPULATION,
            'ga_generations': cls.GA_GENERATIONS,
        }