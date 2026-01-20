# groupe-JVX/src/config.py
from typing import Dict

class Config:
    # === Market Data ===
    TICKER: str = "BTC-USD"
    INTERVAL: str = "1d"
    START_DATE: str = "2018-01-01"
    END_DATE: str = "2026-01-01"
    
    # === Data Split ===
    TRAIN_RATIO: float = 0.70
    TEST_RATIO: float = 0.30
    
    # === Backtesting ===
    # CORRECTION : 1 Million pour pouvoir acheter des BTC entiers (qui valent > 60k$)
    INITIAL_CASH: float = 1_000_000.0
    COMMISSION_CRYPTO: float = 0.001 
    COMMISSION_STOCK: float = 0.0001
    
    @classmethod
    def get_commission(cls) -> float:
        if "BTC" in cls.TICKER or "ETH" in cls.TICKER:
            return cls.COMMISSION_CRYPTO
        return cls.COMMISSION_STOCK
    
    # === Genetic Algorithm ===
    GA_POPULATION: int = 50 
    GA_GENERATIONS: int = 10 
    GA_CXPB: float = 0.7
    GA_MUTPB: float = 0.2
    
    # === Walk-Forward Analysis ===
    WFA_TRAIN_MONTHS: int = 24
    WFA_TEST_MONTHS: int = 6    
    WFA_STEP_MONTHS: int = 3
    
    # === Gene Bounds ===
    # Tuple (min, max) pour le mode "Turbo"
    GENE_BOUNDS: Dict[str, tuple] = {
        'SMA_F': (5, 30),
        'SMA_S': (40, 150),
        'RSI_P': (10, 20),
        'RSI_UP': (65, 85),
        'RSI_LO': (20, 45), # Forcé en survente
        'SL': (0.02, 0.10),     
        'TP': (0.05, 0.30),
    }
    
    # === Paths ===
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"