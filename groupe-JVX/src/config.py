"""
Central configuration module.
"""
from typing import Dict

class Config:
    # === Market Data ===
    TICKER: str = "BTC-USD"
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
        if "BTC" in cls.TICKER or "ETH" in cls.TICKER:
            return cls.COMMISSION_CRYPTO
        return cls.COMMISSION_STOCK
    
    # === Genetic Algorithm ===
    GA_POPULATION: int = 40  # Légèrement réduit pour aller plus vite
    GA_GENERATIONS: int = 8
    GA_CXPB: float = 0.7
    GA_MUTPB: float = 0.2
    
    # === Walk-Forward Analysis ===
    WFA_TRAIN_MONTHS: int = 12
    WFA_TEST_MONTHS: int = 6   # AUGMENTÉ (3->6) pour avoir assez de données
    WFA_STEP_MONTHS: int = 3
    
    # === Gene Bounds ===
    GENE_BOUNDS: Dict[str, tuple] = {
        'SMA_F': (5, 40),       
        'SMA_S': (50, 90),      # RÉDUIT (200->90) pour éviter le crash "IndexError"
        'RSI_P': (5, 25),       
        'RSI_UP': (65, 90),     
        'RSI_LO': (20, 55),     # ÉLARGI (45->55) pour forcer plus d'achats
        'SL': (0.01, 0.15),     
        'TP': (0.02, 0.30),     
    }
    
    # === Paths ===
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"