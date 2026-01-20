"""
Central configuration module.
"""
from typing import Dict, Any

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
    # Frais un peu plus réalistes (0.1%)
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
    WFA_TRAIN_MONTHS: int = 12
    WFA_TEST_MONTHS: int = 3
    WFA_STEP_MONTHS: int = 3
    
    # === Gene Bounds (Assouplis pour garantir des trades) ===
    GENE_BOUNDS: Dict[str, tuple] = {
        'SMA_F': (5, 60),       # Moyenne rapide
        'SMA_S': (70, 200),     # Moyenne lente (doit être > SMA_F)
        'RSI_P': (5, 25),       # Période RSI
        'RSI_UP': (65, 90),     # Seuil surachat
        'RSI_LO': (15, 45),     # Seuil survente (Élargi jusqu'à 45 pour capter + de trades)
        'SL': (0.01, 0.15),     # Stop Loss (1% à 15%)
        'TP': (0.02, 0.30),     # Take Profit (2% à 30%)
    }
    
    # === Paths ===
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"