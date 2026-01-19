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
            df = pd.read_csv(self.cache_file, index_col=0, parse_dates=True)
            return self._sanitize_data(df)
        
        # Download fresh data
        print(f"Downloading {self.ticker} data from {start_date} to {end_date}...")
        try:
            df = yf.download(
                self.ticker,
                start=start_date,
                end=end_date,
                interval=self.interval,
                progress=False
            )
            
            if df.empty:
                raise ValueError(f"No data downloaded for {self.ticker}")
            
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
        # Drop NaN values
        df = df.dropna()
        
        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Sort by date
        df = df.sort_index()
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
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
            raise ValueError(f"No data found between {start_date} and {end_date}")
        
        return sliced_data
    
    def get_full_data(self) -> pd.DataFrame:
        """
        Get the complete dataset from config dates.
        
        Returns:
            pd.DataFrame: Full dataset
        """
        return self.download_data(Config.START_DATE, Config.END_DATE)