"""
Central configuration module.
"""
from typing import Dict

class Config:
    # === Market Data ===
    TICKER: str = "ETH-USD"
    INTERVAL: str = "1d"
    START_DATE: str = "2018-01-01" # On prend plus d'historique pour être large
    END_DATE: str = "2026-01-01"
    
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
    GA_POPULATION: int = 30 
    GA_GENERATIONS: int = 5 
    GA_CXPB: float = 0.7
    GA_MUTPB: float = 0.2
    
    # === Walk-Forward Analysis ===
    WFA_TRAIN_MONTHS: int = 24  # Plus longue période d'entrainement
    WFA_TEST_MONTHS: int = 6    
    WFA_STEP_MONTHS: int = 3
    
    # === Gene Bounds (MODE TURBO / AGRESSIF) ===
    GENE_BOUNDS: Dict[str, tuple] = {
        'SMA_F': (5, 20),       # Très rapide (5 à 20 jours)
        'SMA_S': (25, 60),      # Rapide (max 60 jours pour éviter le warm-up trop long)
        'RSI_P': (5, 14),       # RSI standard ou rapide
        'RSI_UP': (70, 95),     
        'RSI_LO': (30, 65),     # IMPORTANT: On achète même si le RSI est à 65 (presque neutre)
        'SL': (0.02, 0.15),     
        'TP': (0.05, 0.50),     # On vise des gros gains
    }
    
    # === Paths ===
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"