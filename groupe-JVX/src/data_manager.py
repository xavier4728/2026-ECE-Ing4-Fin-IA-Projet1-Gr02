"""
Data management module for downloading and caching market data.
"""
import os
from pathlib import Path
from typing import Optional
import pandas as pd
import yfinance as yf
from src.config import Config


class DataManager:
    """
    Handles downloading, caching, and retrieving market data.
    """
    
    def __init__(self, ticker: str = Config.TICKER, interval: str = Config.INTERVAL):
        """
        Initialize the DataManager.
        
        Args:
            ticker: Stock/crypto ticker symbol
            interval: Data interval (e.g., '1d', '1h')
        """
        self.ticker = ticker
        self.interval = interval
        self.data_dir = Path(Config.DATA_DIR)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_file = self.data_dir / f"{ticker}_{interval}.csv"
        
    def download_data(self, start_date: str, end_date: str, force_download: bool = False) -> pd.DataFrame:
        """
        Download market data from Yahoo Finance with caching.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            force_download: Force re-download even if cached data exists
            
        Returns:
            pd.DataFrame: OHLCV dataframe with DatetimeIndex
        """
        # Check if cached data exists
        if self.cache_file.exists() and not force_download:
            print(f"Loading cached data from {self.cache_file}")
            try:
                df = pd.read_csv(self.cache_file, index_col=0, parse_dates=True)
                return self._sanitize_data(df)
            except Exception as e:
                print(f"Cache corrupted, re-downloading... ({e})")
        
        # Download fresh data
        print(f"Downloading {self.ticker} data from {start_date} to {end_date}...")
        try:
            # CORRECTION : multi_level_index=False évite les colonnes complexes
            df = yf.download(
                self.ticker,
                start=start_date,
                end=end_date,
                interval=self.interval,
                progress=False,
                multi_level_index=False 
            )
            
            if df.empty:
                # Tentative de secours sans les dates si l'API est stricte
                print("Retry downloading without strict dates...")
                df = yf.download(
                    self.ticker,
                    period="5y", # On prend 5 ans par défaut
                    interval=self.interval,
                    progress=False,
                    multi_level_index=False
                )

            if df.empty:
                raise ValueError(f"No data downloaded for {self.ticker}. Ticker might be wrong or API blocked.")
            
            # Save to cache
            df.to_csv(self.cache_file)
            print(f"Data cached to {self.cache_file}")
            
            return self._sanitize_data(df)
            
        except Exception as e:
            print(f"Error downloading data: {e}")
            raise
    
    def _sanitize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and sanitize the dataframe.
        
        Args:
            df: Raw dataframe
            
        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        # CORRECTION : Gestion des MultiIndex (cas où yfinance renvoie (Price, Ticker))
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Drop NaN values
        df = df.dropna()
        
        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Sort by date
        df = df.sort_index()
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Parfois Yahoo renvoie 'Adj Close' au lieu de 'Close', on gère ça
        if 'Adj Close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['Adj Close']

        for col in required_cols:
            if col not in df.columns:
                # Debug print pour aider si ça plante encore
                print(f"Available columns: {df.columns.tolist()}")
                raise ValueError(f"Missing required column: {col}")
        
        return df
    
    def get_data_slice(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get a specific time slice of the data.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            pd.DataFrame: Data slice for the specified period
        """
        # First ensure we have the full dataset
        full_data = self.download_data(Config.START_DATE, Config.END_DATE)
        
        # Slice the data
        mask = (full_data.index >= start_date) & (full_data.index <= end_date)
        sliced_data = full_data[mask].copy()
        
        if sliced_data.empty:
            # Fallback : parfois les dates ne correspondent pas exactement (jours fériés)
            # On essaie d'être plus souple
            return full_data
        
        return sliced_data
    
    def get_full_data(self) -> pd.DataFrame:
        """
        Get the complete dataset from config dates.
        
        Returns:
            pd.DataFrame: Full dataset
        """
        return self.download_data(Config.START_DATE, Config.END_DATE)