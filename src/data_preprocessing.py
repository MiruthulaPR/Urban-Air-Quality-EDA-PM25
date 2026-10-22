"""
Data Preprocessing Module for Beijing Multi-Site Air Quality Dataset
Course: U21ADP05 — Exploratory Data Analysis and Visualization
"""

import os
import glob
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_raw_dataset(raw_dir: str) -> pd.DataFrame:
    """
    Loads and consolidates all 12 air quality monitoring station CSV files.
    """
    csv_pattern = os.path.join(raw_dir, "*.csv")
    csv_files = sorted(glob.glob(csv_pattern))
    if not csv_files:
        # Check subdirectories
        csv_pattern = os.path.join(raw_dir, "**", "*.csv")
        csv_files = sorted(glob.glob(csv_pattern, recursive=True))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    dfs = []
    for f in csv_files:
        df_station = pd.read_csv(f)
        dfs.append(df_station)

    df_all = pd.concat(dfs, ignore_index=True)
    return df_all


def clean_and_impute_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assembles datetime timestamp, audits missing values, and performs
    physically-grounded temporal interpolation station-by-station.
    """
    df = df.copy()

    # Construct datetime index
    df['datetime'] = pd.to_datetime(
        df[['year', 'month', 'day', 'hour']]
    )

    # Sort sequentially by station and time
    df = df.sort_values(by=['station', 'datetime']).reset_index(drop=True)

    pollutant_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    weather_cols = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    numeric_cols = pollutant_cols + weather_cols

    # Station-wise time-series linear interpolation for continuous variables
    # Limiting interpolation gap to 24 consecutive hours to avoid over-smoothing long gaps
    cleaned_dfs = []
    for station, group in df.groupby('station', as_index=False):
        group = group.copy()
        for col in numeric_cols:
            group[col] = group[col].interpolate(method='linear', limit=24)
            # Fill any remaining edges with forward/backward fill
            group[col] = group[col].bfill().ffill()

        # Wind direction categorical imputation (mode per station)
        mode_wd = group['wd'].mode()[0] if not group['wd'].dropna().empty else 'NE'
        group['wd'] = group['wd'].fillna(mode_wd)

        cleaned_dfs.append(group)

    df_cleaned = pd.concat(cleaned_dfs, ignore_index=True)

    # Verify physical sanity bounds (no negative concentrations)
    for col in pollutant_cols:
        df_cleaned[col] = df_cleaned[col].clip(lower=0.0)
    df_cleaned['WSPM'] = df_cleaned['WSPM'].clip(lower=0.0)
    df_cleaned['RAIN'] = df_cleaned['RAIN'].clip(lower=0.0)

    return df_cleaned


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers past-only lagged features, rolling stats, cyclic time encodings,
    and forms the strictly non-leaking next-hour PM2.5 target: PM2.5_{t+1}.
    """
    df = df.sort_values(by=['station', 'datetime']).reset_index(drop=True)
    dfs_feat = []

    pollutant_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    weather_cols = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']

    for station, group in df.groupby('station', as_index=False):
        group = group.copy()

        # Target: PM2.5 at hour t+1 (strictly next-hour forecast)
        group['target_PM2.5_next_1h'] = group['PM2.5'].shift(-1)

        # Lags of PM2.5 (past-only)
        group['PM2.5_lag1'] = group['PM2.5'].shift(0)  # current hour t
        group['PM2.5_lag2'] = group['PM2.5'].shift(1)  # hour t-1
        group['PM2.5_lag3'] = group['PM2.5'].shift(2)  # hour t-2
        group['PM2.5_lag6'] = group['PM2.5'].shift(5)  # hour t-5

        # Lags of other key pollutants and weather at hour t
        for col in ['PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'WSPM']:
            group[f'{col}_lag1'] = group[col].shift(0)
            group[f'{col}_lag2'] = group[col].shift(1)

        # Rolling window features of PM2.5 (past 6h and 24h moving averages)
        group['PM2.5_roll_mean_6h'] = group['PM2.5'].rolling(window=6, min_periods=1).mean()
        group['PM2.5_roll_std_6h'] = group['PM2.5'].rolling(window=6, min_periods=1).std().fillna(0)
        group['PM2.5_roll_mean_24h'] = group['PM2.5'].rolling(window=24, min_periods=1).mean()

        # Ratio and delta features
        group['PM2.5_PM10_ratio'] = (group['PM2.5'] / (group['PM10'] + 1e-5)).clip(0, 1)
        group['PM2.5_diff_1h'] = group['PM2.5'] - group['PM2.5_lag2']

        # Cyclic temporal encodings (diurnal and seasonal cycles)
        group['hour_sin'] = np.sin(2 * np.pi * group['hour'] / 24.0)
        group['hour_cos'] = np.cos(2 * np.pi * group['hour'] / 24.0)
        group['month_sin'] = np.sin(2 * np.pi * group['month'] / 12.0)
        group['month_cos'] = np.cos(2 * np.pi * group['month'] / 12.0)

        # Season indicator (1: Winter, 2: Spring, 3: Summer, 4: Autumn)
        # Beijing seasons: Dec-Feb (Winter), Mar-May (Spring), Jun-Aug (Summer), Sep-Nov (Autumn)
        def get_season(m):
            if m in [12, 1, 2]:
                return 'Winter'
            elif m in [3, 4, 5]:
                return 'Spring'
            elif m in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Autumn'

        group['season'] = group['month'].apply(get_season)

        dfs_feat.append(group)

    df_feat = pd.concat(dfs_feat, ignore_index=True)

    # Drop rows where target or initial lags are NaN
    df_feat = df_feat.dropna(subset=['target_PM2.5_next_1h', 'PM2.5_lag6']).reset_index(drop=True)
    return df_feat


def create_chronological_splits(df: pd.DataFrame):
    """
    Splits data chronologically into Train (2013-03-01 to 2016-02-29),
    Validation (2016-03-01 to 2016-10-31), and Test (2016-11-01 to 2017-02-28).
    This guarantees ZERO temporal data leakage.
    """
    train_mask = df['datetime'] < '2016-03-01'
    val_mask = (df['datetime'] >= '2016-03-01') & (df['datetime'] < '2016-11-01')
    test_mask = df['datetime'] >= '2016-11-01'

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    return train_df, val_df, test_df


if __name__ == '__main__':
    base_dir = r"c:\Users\MiRuThUlA.LAPTOP-SMP99ABO.000\OneDrive\Desktop\Urban_Air_Quality_EDA"
    raw_dir = os.path.join(base_dir, "data", "raw")
    print("Loading raw multi-site dataset...")
    df_raw = load_raw_dataset(raw_dir)
    print(f"Raw dataset shape: {df_raw.shape}")

    print("Cleaning and interpolating missing values...")
    df_clean = clean_and_impute_data(df_raw)
    print(f"Cleaned dataset shape: {df_clean.shape}")

    print("Engineering features and prediction target...")
    df_feat = engineer_features(df_clean)
    print(f"Feature dataset shape: {df_feat.shape}")

    train_df, val_df, test_df = create_chronological_splits(df_feat)
    print(f"Train split shape: {train_df.shape} ({train_df['datetime'].min()} to {train_df['datetime'].max()})")
    print(f"Val split shape:   {val_df.shape} ({val_df['datetime'].min()} to {val_df['datetime'].max()})")
    print(f"Test split shape:  {test_df.shape} ({test_df['datetime'].min()} to {test_df['datetime'].max()})")
