# groupe-JVX/src/backtest_runner.py
from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
from .config import Config  # Import de la config pour le Cash

# --- INDICATEURS PANDAS (PORTABLES) ---
def SMA(array, n):
    return pd.Series(array).rolling(n).mean()

def RSI(array, n):
    series = pd.Series(array)
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/n, min_periods=n, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

# --- STRATEGIE ---
class GenStrategy(Strategy):
    # Paramètres par défaut
    SMA_F, SMA_S, RSI_P, RSI_LO, RSI_UP, SL, TP = 10, 50, 14, 30, 70, 0.05, 0.1
    
    # Paramètre spécial pour le Walk-Forward (Warm-up)
    trading_start_date = None 

    def init(self):
        self.sma_f = self.I(SMA, self.data.Close, self.SMA_F)
        self.sma_s = self.I(SMA, self.data.Close, self.SMA_S)
        self.rsi = self.I(RSI, self.data.Close, self.RSI_P)

    def next(self):
        # 1. Gestion du Warm-up (WFA)
        if self.trading_start_date is not None:
            if pd.Timestamp(self.data.index[-1]) < pd.Timestamp(self.trading_start_date):
                return

        # 2. Gestion du Trading
        price = self.data.Close[-1]
        
        if not self.position:
            # Condition stricte : Tendance + Survente
            if self.sma_f[-1] > self.sma_s[-1] and self.rsi[-1] < self.RSI_LO:
                sl_price = price * (1 - self.SL)
                tp_price = price * (1 + self.TP)
                self.buy(sl=sl_price, tp=tp_price)

def run_backtest_with_params(data_input, params, verbose=False, trading_start_date=None):
    """Exécute le backtest (Compatible DataFrame et Fichier)."""
    try:
        # GESTION CRITIQUE : DataFrame vs Chemin Fichier
        if isinstance(data_input, str):
            data = pd.read_csv(data_input, index_col='Date', parse_dates=True)
        else:
            # Si c'est déjà un DataFrame (cas du main.py)
            data = data_input.copy()
            
        # Nettoyage
        if 'Volume' not in data.columns: data['Volume'] = 0
        data = data.dropna()

        # Vérification taille minimale
        max_lookback = max(params.get('SMA_S', 200), 50)
        if len(data) < max_lookback + 5:
             return {'Return [%]': -100.0, '# Trades': 0, 'Max. Drawdown [%]': 100.0, 'Win Rate [%]': 0.0}

        # Injection dynamique des paramètres
        class IndividualStrategy(GenStrategy):
            SMA_F = int(params['SMA_F'])
            SMA_S = int(params['SMA_S'])
            RSI_P = int(params['RSI_P'])
            RSI_LO = int(params['RSI_LO'])
            RSI_UP = int(params['RSI_UP'])
            SL = float(params['SL'])
            TP = float(params['TP'])
            
        # Injection de la date de démarrage (hack de classe)
        IndividualStrategy.trading_start_date = trading_start_date

        # Backtest avec CASH configuré
        bt = Backtest(data, IndividualStrategy, cash=Config.INITIAL_CASH, commission=0.001)
        stats = bt.run()
        
        if verbose:
            print(stats)

        return stats

    except Exception as e:
        print(f"Erreur Backtest Runner: {e}")
        return {'Return [%]': -100.0, '# Trades': 0, 'Max. Drawdown [%]': 100.0, 'Win Rate [%]': 0.0}

# ALIAS VITAL
run_simple_backtest = run_backtest_with_params