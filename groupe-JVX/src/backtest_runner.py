# groupe-JVX/src/backtest_runner.py
from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# --- DÉFINITION DES INDICATEURS (SANS TA-LIB) ---

def SMA(array, n):
    """
    Moyenne Mobile Simple (Simple Moving Average)
    Calculée via Pandas rolling mean.
    """
    return pd.Series(array).rolling(n).mean()

def RSI(array, n):
    """
    Relative Strength Index (RSI)
    Implémentation vectorisée avec Pandas (Wilder's Smoothing).
    """
    series = pd.Series(array)
    delta = series.diff()
    
    # Séparation des gains et des pertes
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    # Calcul de la moyenne mobile exponentielle (EWM)
    # Note: Pour le RSI, alpha = 1/n correspond au lissage de Wilder standard
    avg_gain = gain.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    
    # Gestion de la division par zéro (si avg_loss est 0)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50) # Valeur neutre pour le début de l'historique

# --- STRATÉGIE ---

class GenStrategy(Strategy):
    # Les paramètres par défaut seront écrasés par l'AG
    SMA_F = 10
    SMA_S = 50
    RSI_P = 14
    RSI_LO = 30
    RSI_UP = 70
    SL = 0.05
    TP = 0.10

    def init(self):
        # Pré-calcul des indicateurs SANS TA-Lib
        # self.I() enregistre la fonction pour qu'elle soit exécutée et plottable
        self.sma_f = self.I(SMA, self.data.Close, self.SMA_F)
        self.sma_s = self.I(SMA, self.data.Close, self.SMA_S)
        self.rsi = self.I(RSI, self.data.Close, self.RSI_P)

    def next(self):
        # Gestion des positions
        price = self.data.Close[-1]

        # Si nous n'avons pas de position, nous cherchons à entrer
        if not self.position:
            # CONDITION D'ACHAT (Long)
            # 1. Tendance haussière (Fast > Slow)
            # 2. Repli temporaire (RSI < Seuil Bas)
            if self.sma_f[-1] > self.sma_s[-1] and self.rsi[-1] < self.RSI_LO:
                
                # Calcul dynamique du SL et TP
                sl_price = price * (1 - self.SL)
                tp_price = price * (1 + self.TP)
                
                self.buy(sl=sl_price, tp=tp_price)

        # Si nous avons une position, nous laissons le SL/TP gérer la sortie
        # ou nous pourrions ajouter une condition de sortie ici.

def run_backtest_with_params(data_path, params):
    """
    Exécute un backtest unique avec les paramètres fournis par l'AG.
    """
    try:
        # Chargement des données
        # On force le parsing des dates pour éviter les erreurs d'index
        data = pd.read_csv(data_path, index_col='Date', parse_dates=True)
        
        # Nettoyage basique
        data = data.dropna()
        
        # Vérification si les données sont suffisantes pour les indicateurs
        max_lookback = max(params.get('SMA_S', 200), params.get('SMA_F', 50))
        if len(data) < max_lookback:
            # Retourne un résultat vide/nul si pas assez de données
            return {'Return [%]': -100, '# Trades': 0, 'Max. Drawdown [%]': 100}

        # Configuration de la stratégie avec les paramètres de l'individu
        # On crée une sous-classe dynamique pour injecter les paramètres
        class IndividualStrategy(GenStrategy):
            SMA_F = int(params['SMA_F'])
            SMA_S = int(params['SMA_S'])
            RSI_P = int(params['RSI_P'])
            RSI_LO = int(params['RSI_LO'])
            RSI_UP = int(params['RSI_UP'])
            SL = float(params['SL'])
            TP = float(params['TP'])

        # Lancement du backtest
        # Cash initial réaliste (ex: 10,000$)
        # Commission standard crypto (0.1% = 0.001)
        bt = Backtest(data, IndividualStrategy, cash=10000, commission=0.001)
        
        stats = bt.run()
        return stats
        
    except Exception as e:
        print(f"Erreur Backtest: {e}")
        # En cas de crash (ex: données corrompues), on retourne un score pénalisant
        return {'Return [%]': -100, '# Trades': 0, 'Max. Drawdown [%]': 100}