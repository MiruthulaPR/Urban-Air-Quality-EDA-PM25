"""
Model Evaluation and Result Visualization Module
Course: U21ADP05 — Exploratory Data Analysis and Visualization
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from train_model import AirQualityMLP, get_feature_columns


def setup_style():
    sns.set_theme(style="whitegrid", font_scale=1.1)
    plt.rcParams['font.sans-serif'] = 'Arial', 'DejaVu Sans', 'Liberation Sans'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['axes.linewidth'] = 0.8


def evaluate_models(base_dir: str):
    models_dir = os.path.join(base_dir, "models")
    output_dir = os.path.join(base_dir, "outputs")
    fig_dir = os.path.join(base_dir, "figures")

    # Load test tensors
    test_bundle = torch.load(os.path.join(models_dir, 'test_tensors.pt'), weights_only=False)
    X_test_t = test_bundle['X_test_t']
    y_test_t = test_bundle['y_test_t']
    test_df = test_bundle['test_df']

    y_test = y_test_t.numpy()

    # Load best model config
    with open(os.path.join(output_dir, 'best_training_history.json'), 'r') as f:
        best_meta = json.load(f)

    with open(os.path.join(output_dir, 'hyperparameter_tuning.json'), 'r') as f:
        tuning_list = json.load(f)

    best_cfg = [c for c in tuning_list if c['config_name'] == best_meta['best_model']][0]
    hidden_layers = best_cfg['hidden_layers']

    # Initialize model and load weights
    input_dim = X_test_t.shape[1]
    mlp = AirQualityMLP(input_dim=input_dim, hidden_layers=hidden_layers)
    mlp.load_state_dict(torch.load(os.path.join(models_dir, 'best_mlp_pm25.pt'), weights_only=True))
    mlp.eval()

    # Predict with MLP
    with torch.no_grad():
        preds_mlp = mlp(X_test_t).numpy()

    # Predict with Ridge Baseline
    ridge = joblib.load(os.path.join(models_dir, 'ridge_baseline.joblib'))
    preds_ridge = ridge.predict(X_test_t.numpy())

    # Persistence Baseline: Previous hour PM2.5 (PM2.5_lag1)
    preds_persist = test_df['PM2.5_lag1'].values

    # Compute Evaluation Metrics
    def calc_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        # Avoid division by zero in MAPE
        mask = y_true > 1.0
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        return round(float(mae), 3), round(float(rmse), 3), round(float(r2), 4), round(float(mape), 2)

    mae_persist, rmse_persist, r2_persist, mape_persist = calc_metrics(y_test, preds_persist)
    mae_ridge, rmse_ridge, r2_ridge, mape_ridge = calc_metrics(y_test, preds_ridge)
    mae_mlp, rmse_mlp, r2_mlp, mape_mlp = calc_metrics(y_test, preds_mlp)

    metrics_df = pd.DataFrame([
        {'Model': 'Persistence Baseline', 'MAE (ug/m3)': mae_persist, 'RMSE (ug/m3)': rmse_persist, 'R2_Score': r2_persist, 'MAPE (%)': mape_persist},
        {'Model': 'Ridge Regression', 'MAE (ug/m3)': mae_ridge, 'RMSE (ug/m3)': rmse_ridge, 'R2_Score': r2_ridge, 'MAPE (%)': mape_ridge},
        {'Model': f"Deep Learning MLP ({best_meta['best_model']})", 'MAE (ug/m3)': mae_mlp, 'RMSE (ug/m3)': rmse_mlp, 'R2_Score': r2_mlp, 'MAPE (%)': mape_mlp}
    ])

    metrics_df.to_csv(os.path.join(output_dir, 'model_evaluation_metrics.csv'), index=False)
    with open(os.path.join(output_dir, 'model_evaluation_metrics.json'), 'w') as f:
        json.dump(metrics_df.to_dict(orient='records'), f, indent=4)

    print("\n--- Held-Out Test Set Performance (Winter 2016-2017) ---")
    print(metrics_df.to_string(index=False))

    # Permutation Feature Importance
    print("\nCalculating Permutation Feature Importance on Test Set...")
    feature_cols = get_feature_columns()
    base_mse = mean_squared_error(y_test, preds_mlp)
    importance_scores = []

    rng = np.random.RandomState(42)
    X_test_np = X_test_t.numpy().copy()

    for i, col in enumerate(feature_cols):
        X_perm = X_test_np.copy()
        X_perm[:, i] = rng.permutation(X_perm[:, i])
        with torch.no_grad():
            preds_perm = mlp(torch.tensor(X_perm, dtype=torch.float32)).numpy()
        perm_mse = mean_squared_error(y_test, preds_perm)
        delta_mse = float(perm_mse - base_mse)
        importance_scores.append({'Feature': col, 'MSE_Increase': delta_mse})

    imp_df = pd.DataFrame(importance_scores).sort_values(by='MSE_Increase', ascending=False).reset_index(drop=True)
    imp_df.to_csv(os.path.join(output_dir, 'permutation_importance.csv'), index=False)

    # Visualizations
    setup_style()

    # 1. Fig 9: Loss vs Epoch
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    train_loss = best_meta['train_loss']
    val_loss = best_meta['val_loss']
    epochs = range(1, len(train_loss) + 1)
    ax.plot(epochs, train_loss, 'o-', color='#1f77b4', lw=2.2, label='Training Loss (MSE)')
    ax.plot(epochs, val_loss, 's--', color='#ff7f0e', lw=2.2, label='Validation Loss (MSE)')
    ax.set_title(f"Deep Learning MLP Training & Validation Loss vs. Epoch ({best_meta['best_model']})", fontsize=12, weight='bold', pad=12)
    ax.set_xlabel("Epoch Number", fontsize=11, weight='bold')
    ax.set_ylabel("Mean Squared Error (MSE Loss)", fontsize=11, weight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig9_loss_vs_epoch.png"), dpi=300)
    plt.close()

    # 2. Fig 10: Actual vs Predicted PM2.5 Scatter
    # Sample 8,000 test points for clean visualization
    sample_idx = rng.choice(len(y_test), size=min(8000, len(y_test)), replace=False)
    y_test_s = y_test[sample_idx]
    preds_mlp_s = preds_mlp[sample_idx]

    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=300)
    ax.scatter(y_test_s, preds_mlp_s, alpha=0.3, color='#2c7bb6', s=14, edgecolors='none', label='Test Predictions')
    # 45-degree line
    max_val = max(np.percentile(y_test_s, 99.8), np.percentile(preds_mlp_s, 99.8))
    ax.plot([0, max_val], [0, max_val], 'r--', lw=2.2, label='Ideal 1:1 Prediction Line')

    ax.text(0.05, 0.90, f"Test $R^2$ = {r2_mlp:.3f}\nTest RMSE = {rmse_mlp:.2f} $\\mu g/m^3$\nTest MAE = {mae_mlp:.2f} $\\mu g/m^3$",
            transform=ax.transAxes, fontsize=11, weight='bold',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#aaaaaa", alpha=0.9))

    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.set_title("Actual vs. Predicted 1-Hour Ahead PM2.5 (Held-Out Test Set)", fontsize=12, weight='bold', pad=12)
    ax.set_xlabel("Actual PM2.5 Concentration ($\\mu g/m^3$)", fontsize=11, weight='bold')
    ax.set_ylabel("Predicted PM2.5 Concentration ($\\mu g/m^3$)", fontsize=11, weight='bold')
    ax.legend(loc='lower right', frameon=True, facecolor='white')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig10_actual_vs_predicted.png"), dpi=300)
    plt.close()

    # 3. Fig 11: Residual Distribution
    residuals = y_test - preds_mlp
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    res_sample = residuals[sample_idx]
    sns.histplot(res_sample, bins=70, kde=True, ax=ax, color='#0571b0', stat='density')
    res_mean = float(np.mean(residuals))
    res_std = float(np.std(residuals))
    res_median = float(np.median(residuals))

    res_stats = {
        'residual_mean': round(res_mean, 4),
        'residual_std': round(res_std, 4),
        'residual_median': round(res_median, 4),
        'residual_min': round(float(np.min(residuals)), 4),
        'residual_max': round(float(np.max(residuals)), 4)
    }
    with open(os.path.join(output_dir, 'model_residual_statistics.json'), 'w') as f:
        json.dump(res_stats, f, indent=4)

    x_grid = np.linspace(np.percentile(res_sample, 0.5), np.percentile(res_sample, 99.5), 200)
    from scipy.stats import norm
    ax.plot(x_grid, norm.pdf(x_grid, res_mean, res_std), 'r--', lw=2.0, label=f'Fitted Normal ($\\mu$={res_mean:.2f}, $\\sigma$={res_std:.2f})')

    ax.set_title("Model Residual Distribution ($y_{actual} - \\hat{y}_{predicted}$)", fontsize=12, weight='bold', pad=12)
    ax.set_xlabel("Residual Error ($\\mu g/m^3$)", fontsize=11, weight='bold')
    ax.set_ylabel("Probability Density", fontsize=11, weight='bold')
    ax.set_xlim(-80, 80)
    ax.legend(frameon=True, facecolor='white')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig11_residual_distribution.png"), dpi=300)
    plt.close()

    # 4. Fig 12: Residuals vs Predicted
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.scatter(preds_mlp_s, residuals[sample_idx], alpha=0.25, color='#7b3294', s=14, edgecolors='none')
    ax.axhline(0, color='red', linestyle='--', lw=2)
    ax.set_title("Residuals vs. Predicted PM2.5 Concentration (Homoscedasticity Diagnostic)", fontsize=12, weight='bold', pad=12)
    ax.set_xlabel("Predicted PM2.5 ($\\mu g/m^3$)", fontsize=11, weight='bold')
    ax.set_ylabel("Residuals ($y - \\hat{y}$, $\\mu g/m^3$)", fontsize=11, weight='bold')
    ax.set_xlim(0, max_val)
    ax.set_ylim(-120, 120)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig12_residuals_vs_predicted.png"), dpi=300)
    plt.close()

    # 5. Fig 13: Model Comparison Metrics
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    x = np.arange(len(metrics_df))
    width = 0.25

    rects1 = ax.bar(x - width, metrics_df['MAE (ug/m3)'], width, label='MAE ($\\mu g/m^3$)', color='#4393c3')
    rects2 = ax.bar(x, metrics_df['RMSE (ug/m3)'], width, label='RMSE ($\\mu g/m^3$)', color='#d66048')
    rects3 = ax.bar(x + width, metrics_df['R2_Score'] * 100, width, label='$R^2$ Score (%)', color='#2ca25f')

    ax.set_ylabel('Metric Score', fontsize=11, weight='bold')
    ax.set_title('Comparative Evaluation: Baselines vs. Deep Learning MLP', fontsize=12, weight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_df['Model'], fontsize=10, weight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.95)

    def autolabel(rects, is_pct=False):
        for rect in rects:
            height = rect.get_height()
            txt = f'{height:.1f}%' if is_pct else f'{height:.1f}'
            ax.annotate(txt,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, weight='bold')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3, is_pct=True)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig13_model_comparison_metrics.png"), dpi=300)
    plt.close()

    # 6. Fig 14: Permutation Feature Importance
    top_imp = imp_df.head(12)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars = ax.barh(top_imp['Feature'][::-1], top_imp['MSE_Increase'][::-1], color=sns.color_palette("flare", len(top_imp)))

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1.0, bar.get_y() + bar.get_height() / 2, f'+{w:.1f}',
                va='center', ha='left', fontsize=9, weight='bold', color='#333333')

    ax.set_title("Top 12 Features Ranked by Permutation Feature Importance (Increase in Test MSE)", fontsize=12, weight='bold', pad=12)
    ax.set_xlabel("Mean Squared Error (MSE) Increase on Held-Out Test Set", fontsize=11, weight='bold')
    ax.set_ylabel("Predictor Variable", fontsize=11, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig14_permutation_feature_importance.png"), dpi=300)
    plt.close()

    print("All model evaluation figures successfully generated in figures/ directory!")


if __name__ == '__main__':
    base_dir = r"c:\Users\MiRuThUlA.LAPTOP-SMP99ABO.000\OneDrive\Desktop\Urban_Air_Quality_EDA"
    evaluate_models(base_dir)
