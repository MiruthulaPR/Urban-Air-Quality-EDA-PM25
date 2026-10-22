"""
Visualization Module for Urban Air Quality Analysis
Course: U21ADP05 — Exploratory Data Analysis and Visualization
Generates high-resolution figures (300 DPI) and interactive Plotly HTML outputs.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, lognorm, gamma, weibull_min
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_preprocessing import load_raw_dataset, clean_and_impute_data


def setup_style():
    sns.set_theme(style="whitegrid", font_scale=1.1)
    plt.rcParams['font.sans-serif'] = 'Arial', 'DejaVu Sans', 'Liberation Sans'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['axes.linewidth'] = 0.8


def plot_fig1_missing_data_profile(df_raw: pd.DataFrame, fig_dir: str):
    """
    Fig 1: Missing Data Percentage across features and monitoring stations.
    """
    setup_style()
    missing_pct = (df_raw.isnull().sum() / len(df_raw)) * 100
    missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    palette = sns.color_palette("mako", len(missing_pct))
    bars = ax.barh(missing_pct.index, missing_pct.values, color=palette)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.1, bar.get_y() + bar.get_height() / 2, f'{w:.2f}%',
                va='center', ha='left', fontsize=9, color='#222222', weight='bold')

    ax.set_xlim(0, max(missing_pct.values) * 1.25)
    ax.set_title("Missing Value Distribution Across Air Quality Features (Total N = 420,768)", fontsize=13, weight='bold', pad=12)
    ax.set_xlabel("Missing Observations (%)", fontsize=11, weight='bold')
    ax.set_ylabel("Atmospheric & Meteorological Features", fontsize=11, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig1_missing_data_profile.png"), dpi=300)
    plt.close()


def plot_fig2_pm25_distribution_and_fits(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 2: Empirical PM2.5 histogram + KDE alongside theoretical distribution fits
    (Normal, Lognormal, Gamma, Weibull).
    """
    setup_style()
    pm25 = df_clean['PM2.5'][df_clean['PM2.5'] > 0].dropna()
    # Representative sample for fitting curves
    sample = pm25.sample(n=min(len(pm25), 25000), random_state=42).values

    x_grid = np.linspace(0.1, 400, 1000)

    # Parametric fits
    norm_p = norm.fit(sample)
    lognorm_p = lognorm.fit(sample)
    gamma_p = gamma.fit(sample)
    weibull_p = weibull_min.fit(sample)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Empirical histogram
    ax.hist(sample, bins=80, density=True, alpha=0.35, color='#4A90E2', label='Empirical Histogram')
    sns.kdeplot(sample, ax=ax, color='#1F4E79', lw=2.2, label='Empirical KDE')

    # Fitted curves
    ax.plot(x_grid, norm.pdf(x_grid, *norm_p), 'r--', lw=1.8, label=f'Normal Fit ($\\mu$={norm_p[0]:.1f}, $\\sigma$={norm_p[1]:.1f})')
    ax.plot(x_grid, lognorm.pdf(x_grid, *lognorm_p), 'g--', lw=1.8, label='Lognormal Fit')
    ax.plot(x_grid, gamma.pdf(x_grid, *gamma_p), 'm-.', lw=2.0, label='Gamma Fit (2nd Best Fit)')
    ax.plot(x_grid, weibull_min.pdf(x_grid, *weibull_p), 'b-', lw=2.4, label='Weibull Fit (Best Fit: Lowest AIC & KS)')

    ax.axvline(75, color='orange', linestyle='--', lw=1.5, label='National Grade II Standard (75 $\\mu g/m^3$)')
    ax.axvline(150, color='darkred', linestyle=':', lw=1.5, label='Severe Pollution Threshold (150 $\\mu g/m^3$)')

    ax.set_xlim(0, 400)
    ax.set_title("Continuous Probability Distribution Fitting of Hourly PM2.5 Concentrations", fontsize=13, weight='bold', pad=12)
    ax.set_xlabel("PM2.5 Concentration ($\\mu g / m^3$)", fontsize=11, weight='bold')
    ax.set_ylabel("Probability Density", fontsize=11, weight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig2_pm25_distribution_and_fits.png"), dpi=300)
    plt.close()


def plot_fig3_pollutant_boxplots_by_station(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 3: PM2.5 and PM10 boxplots across all 12 monitoring stations (Spatial analysis).
    """
    setup_style()
    station_order = df_clean.groupby('station')['PM2.5'].median().sort_values(ascending=False).index

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True, dpi=300)

    # Subplot 1: PM2.5
    sns.boxplot(data=df_clean, x='station', y='PM2.5', order=station_order, ax=axes[0],
                palette='coolwarm', showfliers=False, boxprops=dict(alpha=0.85))
    axes[0].axhline(75, color='red', linestyle='--', lw=1.5, label='National Standard (75 $\\mu g/m^3$)')
    axes[0].set_title("A: Spatial Variation of PM2.5 Concentrations Across 12 Monitoring Stations", fontsize=12, weight='bold')
    axes[0].set_ylabel("PM2.5 ($\\mu g/m^3$)", fontsize=10, weight='bold')
    axes[0].legend(loc='upper right')

    # Subplot 2: PM10
    sns.boxplot(data=df_clean, x='station', y='PM10', order=station_order, ax=axes[1],
                palette='viridis', showfliers=False, boxprops=dict(alpha=0.85))
    axes[1].axhline(150, color='red', linestyle='--', lw=1.5, label='National Standard (150 $\\mu g/m^3$)')
    axes[1].set_title("B: Spatial Variation of PM10 Concentrations Across 12 Monitoring Stations", fontsize=12, weight='bold')
    axes[1].set_ylabel("PM10 ($\\mu g/m^3$)", fontsize=10, weight='bold')
    axes[1].set_xlabel("Monitoring Station", fontsize=11, weight='bold')
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=35, ha='right')
    axes[1].legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig3_pollutant_boxplots_by_station.png"), dpi=300)
    plt.close()


def plot_fig4_correlation_heatmap(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 4: Annotated Correlation Heatmap of atmospheric pollutants and meteorological parameters.
    """
    setup_style()
    cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    corr_matrix = df_clean[cols].corr(method='pearson')

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmin=-1.0, vmax=1.0, center=0,
                annot=True, fmt=".2f", square=True, linewidths=0.6,
                cbar_kws={"shrink": 0.8, "label": "Pearson Correlation Coefficient ($r$)"}, ax=ax)

    ax.set_title("Correlation Heatmap: Criteria Pollutants vs. Meteorological Variables", fontsize=13, weight='bold', pad=14)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig4_correlation_heatmap.png"), dpi=300)
    plt.close()


def plot_fig5_seasonal_and_diurnal_profiles(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 5: Seasonal variation boxplots and 24-hour diurnal cycle of PM2.5 vs Ozone.
    """
    setup_style()
    df = df_clean.copy()
    def get_season(m):
        return 'Winter' if m in [12, 1, 2] else 'Spring' if m in [3, 4, 5] else 'Summer' if m in [6, 7, 8] else 'Autumn'
    df['season'] = df['month'].apply(get_season)
    season_order = ['Spring', 'Summer', 'Autumn', 'Winter']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Subplot 1: Seasonal Boxplot
    sns.boxplot(data=df, x='season', y='PM2.5', order=season_order, ax=ax1,
                palette=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'], showfliers=False)
    ax1.axhline(75, color='red', linestyle='--', label='Grade II Limit (75 $\\mu g/m^3$)')
    ax1.set_title("A: Seasonal PM2.5 Distribution (Beijing)", fontsize=12, weight='bold')
    ax1.set_xlabel("Season", fontsize=11, weight='bold')
    ax1.set_ylabel("PM2.5 ($\\mu g/m^3$)", fontsize=11, weight='bold')
    ax1.legend(loc='upper left')

    # Subplot 2: Diurnal Cycle (PM2.5 vs Ozone)
    diurnal = df.groupby('hour')[['PM2.5', 'O3']].mean().reset_index()

    ax2_twin = ax2.twinx()
    line1 = ax2.plot(diurnal['hour'], diurnal['PM2.5'], color='#d95f02', lw=2.5, marker='o', label='PM2.5 (Mean)')
    line2 = ax2_twin.plot(diurnal['hour'], diurnal['O3'], color='#7570b3', lw=2.5, marker='s', label='Ozone $O_3$ (Mean)')

    ax2.set_xlabel("Hour of Day (0 - 23 Local Time)", fontsize=11, weight='bold')
    ax2.set_ylabel("PM2.5 ($\\mu g/m^3$)", color='#d95f02', fontsize=11, weight='bold')
    ax2_twin.set_ylabel("Ozone $O_3$ ($\\mu g/m^3$)", color='#7570b3', fontsize=11, weight='bold')
    ax2.set_xticks(range(0, 24, 2))
    ax2.set_title("B: 24-Hour Diurnal Cycle of PM2.5 vs. Photochemical Ozone ($O_3$)", fontsize=12, weight='bold')

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig5_seasonal_and_diurnal_profiles.png"), dpi=300)
    plt.close()


def plot_fig6_pm25_vs_meteorology(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 6: Bivariate relationships: PM2.5 vs Wind Speed, Temperature, and Dew Point.
    """
    setup_style()
    sample = df_clean.sample(n=min(len(df_clean), 15000), random_state=42)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=300)

    # 1. PM2.5 vs Wind Speed
    sns.scatterplot(data=sample, x='WSPM', y='PM2.5', alpha=0.25, color='#2b83ba', ax=axes[0], s=12)
    sns.regplot(data=sample, x='WSPM', y='PM2.5', scatter=False, ax=axes[0], color='darkred', order=2)
    axes[0].set_title("A: PM2.5 vs Wind Speed (m/s)\n(Strong Atmospheric Dispersion)", fontsize=11, weight='bold')
    axes[0].set_xlabel("Wind Speed (m/s)", fontsize=10, weight='bold')
    axes[0].set_ylabel("PM2.5 ($\\mu g/m^3$)", fontsize=10, weight='bold')
    axes[0].set_ylim(0, 450)

    # 2. PM2.5 vs Temperature
    sns.scatterplot(data=sample, x='TEMP', y='PM2.5', alpha=0.25, color='#fdae61', ax=axes[1], s=12)
    sns.regplot(data=sample, x='TEMP', y='PM2.5', scatter=False, ax=axes[1], color='darkblue', order=2)
    axes[1].set_title("B: PM2.5 vs Temperature ($^\\circ$C)\n(Winter Inversion vs Summer Mixing)", fontsize=11, weight='bold')
    axes[1].set_xlabel("Temperature ($^\\circ$C)", fontsize=10, weight='bold')
    axes[1].set_ylabel("PM2.5 ($\\mu g/m^3$)", fontsize=10, weight='bold')
    axes[1].set_ylim(0, 450)

    # 3. PM2.5 vs Dew Point
    sns.scatterplot(data=sample, x='DEWP', y='PM2.5', alpha=0.25, color='#abdda4', ax=axes[2], s=12)
    sns.regplot(data=sample, x='DEWP', y='PM2.5', scatter=False, ax=axes[2], color='purple', order=2)
    axes[2].set_title("C: PM2.5 vs Dew Point ($^\\circ$C)\n(Hygroscopic Growth in High Moisture)", fontsize=11, weight='bold')
    axes[2].set_xlabel("Dew Point ($^\\circ$C)", fontsize=10, weight='bold')
    axes[2].set_ylabel("PM2.5 ($\\mu g/m^3$)", fontsize=10, weight='bold')
    axes[2].set_ylim(0, 450)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig6_pm25_vs_meteorology.png"), dpi=300)
    plt.close()


def plot_fig7_multisite_spatial_trend(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 7: Monthly long-term trend comparing Urban core vs Suburban stations.
    """
    setup_style()
    df = df_clean.copy()
    urban_stations = ['Dongsi', 'Guanyuan', 'Wanliu', 'Aotizhongxin']
    suburban_stations = ['Dingling', 'Huairou', 'Changping', 'Shunyi']

    df['Region'] = 'Other'
    df.loc[df['station'].isin(urban_stations), 'Region'] = 'Urban Core (Heavy Traffic/Density)'
    df.loc[df['station'].isin(suburban_stations), 'Region'] = 'Suburban/Rural (Background)'

    df_filtered = df[df['Region'] != 'Other'].copy()
    monthly = df_filtered.groupby(['datetime_month', 'Region'])['PM2.5'].mean().reset_index() if 'datetime_month' in df_filtered else None

    # Group by year-month
    df_filtered['YearMonth'] = df_filtered['datetime'].dt.to_period('M').dt.to_timestamp()
    monthly = df_filtered.groupby(['YearMonth', 'Region'])['PM2.5'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    sns.lineplot(data=monthly, x='YearMonth', y='PM2.5', hue='Region', lw=2.2,
                 palette=['#d7191c', '#2b83ba'], ax=ax)

    ax.axhline(75, color='gray', linestyle='--', lw=1.2, label='National Standard (75 $\\mu g/m^3$)')
    ax.set_title("Long-Term Monthly PM2.5 Trajectory: Urban Core vs. Suburban Background (2013-2017)", fontsize=13, weight='bold', pad=12)
    ax.set_xlabel("Date (Monthly Aggregation)", fontsize=11, weight='bold')
    ax.set_ylabel("Monthly Mean PM2.5 ($\\mu g/m^3$)", fontsize=11, weight='bold')
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig7_multisite_spatial_trend.png"), dpi=300)
    plt.close()


def generate_fig8_interactive_air_quality(df_clean: pd.DataFrame, fig_dir: str):
    """
    Fig 8: Interactive Plotly Dashboard saved as HTML (Stage 7: Interact).
    Features interactive time-series brushing, multi-pollutant hover cards, and range selector.
    """
    # Sample daily averages for Aotizhongxin and Dingling to create a responsive, rich interactive widget
    df = df_clean[df_clean['station'].isin(['Aotizhongxin', 'Dingling'])].copy()
    df['date'] = df['datetime'].dt.date
    daily = df.groupby(['station', 'date'])[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'WSPM']].mean().reset_index()
    daily['date'] = pd.to_datetime(daily['date'])

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            "Interactive Particulate Matter Trajectory (PM2.5 & PM10)",
            "Gaseous Precursors & Meteorology (O3 & Wind Speed)"
        )
    )

    # Station Aotizhongxin (Urban)
    aoti = daily[daily['station'] == 'Aotizhongxin']
    fig.add_trace(
        go.Scatter(x=aoti['date'], y=aoti['PM2.5'], mode='lines', name='Aotizhongxin PM2.5',
                   line=dict(color='#e41a1c', width=1.8),
                   hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>PM2.5:</b> %{y:.1f} μg/m³<extra></extra>"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=aoti['date'], y=aoti['PM10'], mode='lines', name='Aotizhongxin PM10',
                   line=dict(color='#ff7f00', width=1.2, dash='dot'),
                   hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>PM10:</b> %{y:.1f} μg/m³<extra></extra>"),
        row=1, col=1
    )

    # Station Dingling (Suburban Background)
    ding = daily[daily['station'] == 'Dingling']
    fig.add_trace(
        go.Scatter(x=ding['date'], y=ding['PM2.5'], mode='lines', name='Dingling PM2.5 (Suburban)',
                   line=dict(color='#377eb8', width=1.8),
                   hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>PM2.5:</b> %{y:.1f} μg/m³<extra></extra>"),
        row=1, col=1
    )

    # Subplot 2: Ozone and Wind Speed
    fig.add_trace(
        go.Scatter(x=aoti['date'], y=aoti['O3'], mode='lines', name='Aotizhongxin O3',
                   line=dict(color='#984ea3', width=1.5),
                   hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Ozone O3:</b> %{y:.1f} μg/m³<extra></extra>"),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=aoti['date'], y=aoti['WSPM'], mode='lines', name='Wind Speed (m/s)',
                   line=dict(color='#4daf4a', width=1.2),
                   hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Wind Speed:</b> %{y:.1f} m/s<extra></extra>"),
        row=2, col=1
    )

    fig.update_layout(
        title="Interactive Exploration: Multi-Site Air Quality Dynamics (2013-2017)",
        title_font_size=15,
        hovermode="x unified",
        template="plotly_white",
        height=650,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Range slider on the bottom x-axis
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        row=2, col=1
    )

    fig.update_yaxes(title_text="Concentration (μg/m³)", row=1, col=1)
    fig.update_yaxes(title_text="Level (μg/m³ / m/s)", row=2, col=1)

    html_path = os.path.join(fig_dir, "fig8_interactive_air_quality.html")
    fig.write_html(html_path)
    print(f"Interactive Plotly dashboard saved to {html_path}")


def run_all_visualizations(base_dir: str):
    raw_dir = os.path.join(base_dir, "data", "raw")
    fig_dir = os.path.join(base_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    print("Loading data for visualization...")
    df_raw = load_raw_dataset(raw_dir)
    print("Generating Fig 1: Missing Data Profile...")
    plot_fig1_missing_data_profile(df_raw, fig_dir)

    print("Cleaning data for statistical plots...")
    df_clean = clean_and_impute_data(df_raw)

    print("Generating Fig 2: PM2.5 Distribution & Probability Fits...")
    plot_fig2_pm25_distribution_and_fits(df_clean, fig_dir)

    print("Generating Fig 3: Multi-Station Boxplots...")
    plot_fig3_pollutant_boxplots_by_station(df_clean, fig_dir)

    print("Generating Fig 4: Correlation Heatmap...")
    plot_fig4_correlation_heatmap(df_clean, fig_dir)

    print("Generating Fig 5: Seasonal & Diurnal Profiles...")
    plot_fig5_seasonal_and_diurnal_profiles(df_clean, fig_dir)

    print("Generating Fig 6: PM2.5 vs Meteorology...")
    plot_fig6_pm25_vs_meteorology(df_clean, fig_dir)

    print("Generating Fig 7: Multi-Site Long Term Trend...")
    plot_fig7_multisite_spatial_trend(df_clean, fig_dir)

    print("Generating Fig 8: Interactive Plotly Dashboard...")
    generate_fig8_interactive_air_quality(df_clean, fig_dir)
    print("All primary EDA visualizations generated successfully!")


if __name__ == '__main__':
    base_dir = r"c:\Users\MiRuThUlA.LAPTOP-SMP99ABO.000\OneDrive\Desktop\Urban_Air_Quality_EDA"
    run_all_visualizations(base_dir)
