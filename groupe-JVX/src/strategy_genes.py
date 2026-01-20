"""
Backtrader strategy implementation with genetic algorithm parameters.
"""
import backtrader as bt
from typing import Dict

class GeneticStrategy(bt.Strategy):
    """
    Trading strategy with parameters optimized by genetic algorithm.
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
        """Initialize strategy indicators."""
        # Validation basique des périodes
        self.valid_params = self.params.SMA_F < self.params.SMA_S
        
        # Indicateurs
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.data.close, period=int(self.params.SMA_F)
        )
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.data.close, period=int(self.params.SMA_S)
        )
        self.rsi = bt.indicators.RSI(
            self.data.close, period=int(self.params.RSI_P)
        )
        
        self.order = None
        
    def notify_order(self, order):
        """Gère les notifications d'ordres (achat/vente/rejet)."""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.order = None
    
    def next(self):
        """Logique exécutée à chaque bougie."""
        # 1. Sécurité : Si paramètres invalides ou ordre en cours, on ne fait rien
        if not self.valid_params or self.order:
            return
        
        # 2. Logique d'Entrée (ACHAT)
        if not self.position:
            # CORRECTION MAJEURE ICI :
            # On achète le "Dip" (RSI bas) dans une tendance haussière (Fast > Slow).
            # On a RETIRÉ la condition (Close > Fast) qui bloquait tout.
            if (self.sma_fast[0] > self.sma_slow[0] and 
                self.rsi[0] < self.params.RSI_LO):
                
                # Calcul Stop Loss / Take Profit
                price = self.data.close[0]
                stop_price = price * (1.0 - self.params.SL)
                limit_price = price * (1.0 + self.params.TP)
                
                # Ordre Bracket (Entrée + SL + TP liés)
                self.order = self.buy_bracket(
                    limitprice=limit_price, 
                    stopprice=stop_price,
                    exectype=bt.Order.Market
                )
        
        # 3. Logique de Sortie (VENTE FORCEE)
        # Note: Le Bracket gère déjà SL/TP, ici on gère juste la sortie technique
        else:
            # On sort si le RSI explose ou si la tendance s'inverse
            if (self.rsi[0] > self.params.RSI_UP or 
                self.sma_fast[0] < self.sma_slow[0]):
                self.close()

def decode_chromosome(chromosome: list) -> Dict[str, float]:
    """Decode a chromosome (list of genes) into strategy parameters."""
    return {
        'SMA_F': int(chromosome[0]),
        'SMA_S': int(chromosome[1]),
        'RSI_P': int(chromosome[2]),
        'RSI_UP': int(chromosome[3]),
        'RSI_LO': int(chromosome[4]),
        'SL': float(chromosome[5]),
        'TP': float(chromosome[6]),
    }