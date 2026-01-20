"""
Data management module for downloading and caching market data.
"""
import os
from pathlib import Path
import pandas as pd
import yfinance as yf
from src.config import Config

class DataManager:
    """Handles downloading, caching, and retrieving market data."""
    
    def __init__(self, ticker: str = Config.TICKER, interval: str = Config.INTERVAL):
        self.ticker = ticker
        self.interval = interval
        self.data_dir = Path(Config.DATA_DIR)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_file = self.data_dir / f"{ticker}_{interval}.csv"
        
    def download_data(self, start_date: str, end_date: str, force_download: bool = False) -> pd.DataFrame:
        """Download market data from Yahoo Finance with caching."""
        if self.cache_file.exists() and not force_download:
            print(f"Loading cached data from {self.cache_file}")
            try:
                df = pd.read_csv(self.cache_file, index_col=0, parse_dates=True)
                return self._sanitize_data(df)
            except Exception:
                print("Cache corrupted, re-downloading...")
        
        print(f"Downloading {self.ticker} data from {start_date} to {end_date}...")
        try:
            # Patch pour la nouvelle version de yfinance
            df = yf.download(
                self.ticker, start=start_date, end=end_date, 
                interval=self.interval, progress=False, multi_level_index=False
            )
            
            if df.empty:
                # Tentative fallback (parfois nécessaire pour les cryptos)
                df = yf.download(
                    self.ticker, period="5y", interval=self.interval, 
                    progress=False, multi_level_index=False
                )

            if df.empty:
                raise ValueError(f"No data for {self.ticker}")
            
            df.to_csv(self.cache_file)
            return self._sanitize_data(df)
            
        except Exception as e:
            print(f"Error downloading data: {e}")
            # Retourner un DataFrame vide sécurisé pour éviter le crash total
            return pd.DataFrame()
    
    def _sanitize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and sanitize the dataframe."""
        # Aplatir les colonnes MultiIndex si nécessaire
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna()
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        df = df.sort_index()
        
        # Gestion Adj Close vs Close
        if 'Adj Close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['Adj Close']
            
        # Vérification minimale
        required = ['Open', 'High', 'Low', 'Close']
        for col in required:
            if col not in df.columns:
                 # Tentative de réparation (cas fréquents avec CSV malformés)
                 df = df.rename(columns=str.capitalize)
        
        return df
    
    def get_full_data(self) -> pd.DataFrame:
        return self.download_data(Config.START_DATE, Config.END_DATE)
        
    def get_data_slice(self, start_date: str, end_date: str) -> pd.DataFrame:
        full_data = self.get_full_data()
        if full_data.empty:
            return full_data
        mask = (full_data.index >= start_date) & (full_data.index <= end_date)
        return full_data[mask].copy()