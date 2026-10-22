"""
Deep Learning Model Training Module (PyTorch MLP)
Course: U21ADP05 — Exploratory Data Analysis and Visualization
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

from data_preprocessing import load_raw_dataset, clean_and_impute_data, engineer_features, create_chronological_splits


class AirQualityMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_layers: list, dropout_rate: float = 0.15):
        super(AirQualityMLP, self).__init__()
        layers = []
        in_dim = input_dim

        for h_dim in hidden_layers:
            layers.append(nn.Linear(in_dim, h_dim))
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            in_dim = h_dim

        # Final regression output
        layers.append(nn.Linear(in_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x).squeeze(-1)


def get_feature_columns():
    return [
        'PM2.5_lag1', 'PM2.5_lag2', 'PM2.5_lag3', 'PM2.5_lag6',
        'PM10_lag1', 'PM10_lag2',
        'SO2_lag1', 'NO2_lag1', 'CO_lag1', 'O3_lag1',
        'TEMP_lag1', 'PRES_lag1', 'DEWP_lag1', 'WSPM_lag1',
        'PM2.5_roll_mean_6h', 'PM2.5_roll_std_6h', 'PM2.5_roll_mean_24h',
        'PM2.5_PM10_ratio', 'PM2.5_diff_1h',
        'hour_sin', 'hour_cos', 'month_sin', 'month_cos'
    ]


def train_single_mlp(
    X_train_tensor, y_train_tensor,
    X_val_tensor, y_val_tensor,
    hidden_layers, lr=1e-3, epochs=25, batch_size=512, patience=5
):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_dim = X_train_tensor.shape[1]

    model = AirQualityMLP(input_dim=input_dim, hidden_layers=hidden_layers).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    best_val_loss = float('inf')
    best_weights = None
    epochs_no_improve = 0
    history = {'train_loss': [], 'val_loss': []}

    for epoch in range(epochs):
        model.train()
        train_losses = []
        for x_b, y_b in train_loader:
            x_b, y_b = x_b.to(device), y_b.to(device)
            optimizer.zero_grad()
            preds = model(x_b)
            loss = criterion(preds, y_b)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        avg_train_loss = float(np.mean(train_losses))

        # Validation
        model.eval()
        val_losses = []
        with torch.no_grad():
            for x_b, y_b in val_loader:
                x_b, y_b = x_b.to(device), y_b.to(device)
                preds = model(x_b)
                loss = criterion(preds, y_b)
                val_losses.append(loss.item())

        avg_val_loss = float(np.mean(val_losses))
        scheduler.step(avg_val_loss)

        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_weights = model.state_dict().copy()
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                break

    if best_weights is not None:
        model.load_state_dict(best_weights)

    return model, history, best_val_loss


def run_training_pipeline(base_dir: str):
    raw_dir = os.path.join(base_dir, "data", "raw")
    output_dir = os.path.join(base_dir, "outputs")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    print("Loading and preparing features for model training...")
    df_raw = load_raw_dataset(raw_dir)
    df_clean = clean_and_impute_data(df_raw)
    df_feat = engineer_features(df_clean)

    train_df, val_df, test_df = create_chronological_splits(df_feat)
    feature_cols = get_feature_columns()
    target_col = 'target_PM2.5_next_1h'

    # Save splits metadata
    split_meta = {
        'train_samples': len(train_df),
        'val_samples': len(val_df),
        'test_samples': len(test_df),
        'features': feature_cols,
        'target': target_col,
        'train_date_range': [str(train_df['datetime'].min()), str(train_df['datetime'].max())],
        'val_date_range': [str(val_df['datetime'].min()), str(val_df['datetime'].max())],
        'test_date_range': [str(test_df['datetime'].min()), str(test_df['datetime'].max())]
    }
    with open(os.path.join(output_dir, 'dataset_split_meta.json'), 'w') as f:
        json.dump(split_meta, f, indent=4)

    # Scale features strictly on train data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(train_df[feature_cols].values)
    X_val_scaled = scaler.transform(val_df[feature_cols].values)
    X_test_scaled = scaler.transform(test_df[feature_cols].values)

    joblib.dump(scaler, os.path.join(models_dir, 'scaler.joblib'))

    y_train = train_df[target_col].values.astype(np.float32)
    y_val = val_df[target_col].values.astype(np.float32)
    y_test = test_df[target_col].values.astype(np.float32)

    # Convert to PyTorch Tensors
    X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    X_val_t = torch.tensor(X_val_scaled, dtype=torch.float32)
    y_val_t = torch.tensor(y_val, dtype=torch.float32)
    X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32)

    # 1. Baseline Model 1: Persistence Baseline (PM2.5 at t)
    # Target is next hour PM2.5, persistence predicts current PM2.5
    y_val_persist = val_df['PM2.5_lag1'].values
    val_persist_mse = float(np.mean((y_val - y_val_persist) ** 2))
    val_persist_mae = float(np.mean(np.abs(y_val - y_val_persist)))

    # 2. Baseline Model 2: Ridge Regression
    ridge = Ridge(alpha=10.0)
    ridge.fit(X_train_scaled, y_train)
    y_val_ridge = ridge.predict(X_val_scaled)
    val_ridge_mse = float(np.mean((y_val - y_val_ridge) ** 2))
    val_ridge_mae = float(np.mean(np.abs(y_val - y_val_ridge)))
    joblib.dump(ridge, os.path.join(models_dir, 'ridge_baseline.joblib'))

    # 3. Deep Learning Hyperparameter Tuning: 3 Architectures
    configs = [
        {'name': 'MLP_Small', 'hidden': [64, 32], 'lr': 1e-3},
        {'name': 'MLP_Medium', 'hidden': [128, 64, 32], 'lr': 1e-3},
        {'name': 'MLP_Large', 'hidden': [256, 128, 64], 'lr': 5e-4}
    ]

    tuning_results = []
    best_overall_val_loss = float('inf')
    best_model_name = None
    best_model = None
    best_history = None

    print("\n--- Commencing Deep Learning Hyperparameter Tuning ---")
    for cfg in configs:
        print(f"Training {cfg['name']} (Architecture: {cfg['hidden']}, LR: {cfg['lr']})...")
        model, hist, val_mse = train_single_mlp(
            X_train_t, y_train_t, X_val_t, y_val_t,
            hidden_layers=cfg['hidden'], lr=cfg['lr'], epochs=20, batch_size=512, patience=4
        )
        val_rmse = float(np.sqrt(val_mse))

        res = {
            'config_name': cfg['name'],
            'hidden_layers': cfg['hidden'],
            'learning_rate': cfg['lr'],
            'val_mse': round(val_mse, 3),
            'val_rmse': round(val_rmse, 3),
            'epochs_trained': len(hist['train_loss'])
        }
        tuning_results.append(res)
        print(f"-> {cfg['name']}: Val MSE = {val_mse:.2f}, Val RMSE = {val_rmse:.2f} ug/m3")

        if val_mse < best_overall_val_loss:
            best_overall_val_loss = val_mse
            best_model_name = cfg['name']
            best_model = model
            best_history = hist

    # Save tuning summary
    with open(os.path.join(output_dir, 'hyperparameter_tuning.json'), 'w') as f:
        json.dump(tuning_results, f, indent=4)

    # Save best model
    torch.save(best_model.state_dict(), os.path.join(models_dir, 'best_mlp_pm25.pt'))

    # Save best training history
    with open(os.path.join(output_dir, 'best_training_history.json'), 'w') as f:
        json.dump({
            'best_model': best_model_name,
            'train_loss': [round(x, 3) for x in best_history['train_loss']],
            'val_loss': [round(x, 3) for x in best_history['val_loss']]
        }, f, indent=4)

    # Save processed test tensors for evaluation
    torch.save({
        'X_test_t': X_test_t,
        'y_test_t': y_test_t,
        'test_df': test_df[['datetime', 'station', 'PM2.5_lag1', target_col]]
    }, os.path.join(models_dir, 'test_tensors.pt'))

    print(f"\nTuning complete! Best architecture: {best_model_name} (Val MSE = {best_overall_val_loss:.2f})")
    print(f"Baselines - Persistence Val MSE: {val_persist_mse:.2f}, Ridge Val MSE: {val_ridge_mse:.2f}")


if __name__ == '__main__':
    base_dir = r"c:\Users\MiRuThUlA.LAPTOP-SMP99ABO.000\OneDrive\Desktop\Urban_Air_Quality_EDA"
    run_training_pipeline(base_dir)
