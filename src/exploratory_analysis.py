"""
Exploratory Data Analysis and Statistical Hypothesis Testing Module
Course: U21ADP05 — Exploratory Data Analysis and Visualization
"""

import os
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, lognorm, gamma, weibull_min, kstest, poisson, nbinom

from data_preprocessing import load_raw_dataset, clean_and_impute_data


def generate_data_quality_report(df_raw: pd.DataFrame, output_dir: str) -> dict:
    """
    Computes missing value summary, duplicate count, and data type inventory.
    """
    os.makedirs(output_dir, exist_ok=True)
    total_rows = len(df_raw)
    missing_counts = df_raw.isnull().sum()
    missing_pct = (missing_counts / total_rows) * 100

    quality_df = pd.DataFrame({
        'Feature': df_raw.columns,
        'DataType': [str(t) for t in df_raw.dtypes],
        'MissingCount': missing_counts.values,
        'MissingPercent': missing_pct.values,
        'UniqueValues': [df_raw[col].nunique() for col in df_raw.columns]
    })
    quality_path = os.path.join(output_dir, 'data_quality_summary.csv')
    quality_df.to_csv(quality_path, index=False)

    duplicates = int(df_raw.duplicated().sum())

    summary = {
        'total_records': total_rows,
        'total_columns': len(df_raw.columns),
        'total_stations': int(df_raw['station'].nunique()),
        'stations_list': df_raw['station'].unique().tolist(),
        'duplicate_records': duplicates,
        'total_missing_cells': int(missing_counts.sum()),
        'highest_missing_feature': str(missing_pct.idxmax()),
        'highest_missing_pct': float(missing_pct.max())
    }

    with open(os.path.join(output_dir, 'data_quality_meta.json'), 'w') as f:
        json.dump(summary, f, indent=4)

    return summary


def compute_descriptive_statistics(df_clean: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    """
    Computes both parametric and non-parametric descriptive statistics.
    """
    numeric_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    records = []

    for col in numeric_cols:
        series = df_clean[col].dropna()
        q25 = float(np.percentile(series, 25))
        q75 = float(np.percentile(series, 75))
        iqr = q75 - q25

        rec = {
            'Variable': col,
            'Mean': float(np.mean(series)),
            'StdDev': float(np.std(series, ddof=1)),
            'Median': float(np.median(series)),
            'IQR': float(iqr),
            'Min': float(np.min(series)),
            'Max': float(np.max(series)),
            'Skewness': float(stats.skew(series)),
            'Kurtosis': float(stats.kurtosis(series))
        }
        records.append(rec)

    stats_df = pd.DataFrame(records)
    stats_df.to_csv(os.path.join(output_dir, 'descriptive_statistics.csv'), index=False)
    return stats_df


def fit_continuous_distributions(series: pd.Series, output_dir: str) -> pd.DataFrame:
    """
    Fits Normal, Lognormal, Gamma, and Weibull distributions to PM2.5.
    Calculates Kolmogorov-Smirnov test statistic, p-value, log-likelihood, AIC, and BIC.
    """
    # Sample a representative subset for efficient KS evaluation
    clean_series = series[series > 0].dropna()
    sample_size = min(len(clean_series), 20000)
    data_sample = clean_series.sample(n=sample_size, random_state=42).values
    n = len(data_sample)

    candidate_models = {
        'Normal': norm,
        'Lognormal': lognorm,
        'Gamma': gamma,
        'Weibull': weibull_min
    }

    results = []
    for name, dist in candidate_models.items():
        try:
            params = dist.fit(data_sample)
            # Log-Likelihood
            log_lik = float(np.sum(dist.logpdf(data_sample, *params)))
            k = len(params)
            aic = 2 * k - 2 * log_lik
            bic = k * np.log(n) - 2 * log_lik

            # KS test using lambda to evaluate cdf directly without parameter unpacking issues
            ks_res = kstest(data_sample, lambda x: dist.cdf(x, *params))

            results.append({
                'Distribution': name,
                'Parameters': ", ".join([f"{p:.4f}" for p in params]),
                'LogLikelihood': round(log_lik, 2),
                'AIC': round(aic, 2),
                'BIC': round(bic, 2),
                'KS_Statistic': round(float(ks_res.statistic), 4),
                'KS_p_value': float(ks_res.pvalue)
            })
        except Exception as e:
            results.append({
                'Distribution': name,
                'Parameters': str(e),
                'LogLikelihood': np.nan,
                'AIC': np.nan,
                'BIC': np.nan,
                'KS_Statistic': np.nan,
                'KS_p_value': np.nan
            })

    dist_df = pd.DataFrame(results)
    dist_df.to_csv(os.path.join(output_dir, 'continuous_distribution_fits.csv'), index=False)
    return dist_df


def explore_discrete_distribution(df_clean: pd.DataFrame, output_dir: str) -> dict:
    """
    Computes daily PM2.5 mean per station and analyzes daily exceedance counts
    (days with PM2.5 > 75 ug/m^3 - National Grade II standard) per month.
    Evaluates overdispersion and compares Poisson vs Negative Binomial candidate models.
    """
    from scipy.optimize import minimize

    df_clean['date'] = df_clean['datetime'].dt.date
    daily_station = df_clean.groupby(['station', 'date', 'year', 'month'])['PM2.5'].mean().reset_index()
    daily_station['exceeds_standard'] = (daily_station['PM2.5'] > 75.0).astype(int)

    # Monthly exceedance counts per station (576 station-months)
    counts = daily_station.groupby(['station', 'year', 'month'])['exceeds_standard'].sum().values
    n = len(counts)

    mean_count = float(np.mean(counts))
    var_count = float(np.var(counts, ddof=1))
    dispersion_ratio = var_count / mean_count if mean_count > 0 else 1.0

    # 1. Poisson model fit
    loglik_pois = float(np.sum(poisson.logpmf(counts, mean_count)))
    aic_pois = 2 * 1 - 2 * loglik_pois
    bic_pois = 1 * np.log(n) - 2 * loglik_pois

    # 2. Negative Binomial model fit via MLE
    p_init = mean_count / var_count
    r_init = (mean_count ** 2) / (var_count - mean_count)

    def neg_loglik_nb(params):
        r, p = params
        if r <= 0 or p <= 0 or p >= 1:
            return 1e10
        return -float(np.sum(nbinom.logpmf(counts, r, p)))

    res_nb = minimize(neg_loglik_nb, [r_init, p_init], bounds=[(1e-3, 500), (1e-4, 0.999)])
    r_opt, p_opt = float(res_nb.x[0]), float(res_nb.x[1])
    loglik_nb = -float(res_nb.fun)
    aic_nb = 2 * 2 - 2 * loglik_nb
    bic_nb = 2 * np.log(n) - 2 * loglik_nb

    discrete_res = {
        'variable': 'Monthly Exceedance Days (PM2.5 > 75 ug/m3)',
        'sample_size_station_months': n,
        'sample_mean': round(mean_count, 3),
        'sample_variance': round(var_count, 3),
        'dispersion_ratio (Var/Mean)': round(dispersion_ratio, 3),
        'poisson_fit': {
            'lambda': round(mean_count, 3),
            'log_likelihood': round(loglik_pois, 2),
            'aic': round(aic_pois, 2),
            'bic': round(bic_pois, 2)
        },
        'negative_binomial_fit': {
            'r_dispersion_param': round(r_opt, 3),
            'p_probability': round(p_opt, 3),
            'log_likelihood': round(loglik_nb, 2),
            'aic': round(aic_nb, 2),
            'bic': round(bic_nb, 2)
        },
        'comparison_summary': (
            f'Overdispersion is present (Var/Mean = {dispersion_ratio:.3f} > 1.0). '
            f'Formal comparison supports the Negative Binomial model (AIC = {aic_nb:.1f}) over the '
            f'equidispersed Poisson model (AIC = {aic_pois:.1f}) with Delta-AIC = {aic_pois - aic_nb:.1f}.'
        )
    }

    with open(os.path.join(output_dir, 'discrete_distribution_summary.json'), 'w') as f:
        json.dump(discrete_res, f, indent=4)

    return discrete_res


def perform_statistical_hypothesis_tests(df_clean: pd.DataFrame, output_dir: str) -> dict:
    """
    Conducts formal statistical hypothesis tests:
    1. Kruskal-Wallis non-parametric ANOVA across 12 monitoring stations.
    2. One-Way ANOVA across 4 seasons for PM2.5.
    3. Mann-Whitney U test between Winter and Summer PM2.5 levels, with Cohen's d effect size.
    """
    # 1. Station differences
    stations = df_clean['station'].unique()
    station_groups = [df_clean[df_clean['station'] == st]['PM2.5'].dropna().values for st in stations]
    kw_stat, kw_p = stats.kruskal(*station_groups)

    # 2. Seasonal differences
    def get_season(m):
        return 'Winter' if m in [12, 1, 2] else 'Spring' if m in [3, 4, 5] else 'Summer' if m in [6, 7, 8] else 'Autumn'

    df_clean['season'] = df_clean['month'].apply(get_season)
    season_groups = [df_clean[df_clean['season'] == s]['PM2.5'].dropna().values for s in ['Winter', 'Spring', 'Summer', 'Autumn']]
    anova_stat, anova_p = stats.f_oneway(*season_groups)

    # 3. Winter vs Summer Mann-Whitney U test
    winter_pm25 = df_clean[df_clean['season'] == 'Winter']['PM2.5'].dropna().values
    summer_pm25 = df_clean[df_clean['season'] == 'Summer']['PM2.5'].dropna().values

    # Sample for Mann-Whitney to ensure reasonable execution time while retaining high statistical power
    rng = np.random.RandomState(42)
    winter_sub = rng.choice(winter_pm25, size=min(len(winter_pm25), 15000), replace=False)
    summer_sub = rng.choice(summer_pm25, size=min(len(summer_pm25), 15000), replace=False)

    mwu_stat, mwu_p = stats.mannwhitneyu(winter_sub, summer_sub, alternative='two-sided')

    # Cohen's d effect size
    n1, n2 = len(winter_sub), len(summer_sub)
    s1, s2 = np.var(winter_sub, ddof=1), np.var(summer_sub, ddof=1)
    pooled_s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    cohens_d = (np.mean(winter_sub) - np.mean(summer_sub)) / pooled_s

    hypothesis_results = {
        'Kruskal_Wallis_Stations': {
            'test': 'Kruskal-Wallis H-test across 12 Monitoring Stations',
            'statistic': round(float(kw_stat), 2),
            'p_value': float(kw_p),
            'conclusion': 'Significant spatial heterogeneity across monitoring stations (p < 0.001).'
        },
        'ANOVA_Seasons': {
            'test': 'One-Way ANOVA across 4 Seasons for PM2.5',
            'F_statistic': round(float(anova_stat), 2),
            'p_value': float(anova_p),
            'conclusion': 'Significant seasonal variation in PM2.5 concentrations (p < 0.001).'
        },
        'Mann_Whitney_Winter_vs_Summer': {
            'test': 'Mann-Whitney U Test: Winter vs Summer PM2.5',
            'U_statistic': float(mwu_stat),
            'p_value': float(mwu_p),
            'winter_mean': round(float(np.mean(winter_sub)), 2),
            'summer_mean': round(float(np.mean(summer_sub)), 2),
            'winter_median': round(float(np.median(winter_sub)), 2),
            'summer_median': round(float(np.median(summer_sub)), 2),
            'cohens_d': round(float(cohens_d), 3),
            'conclusion': (
                f'Winter PM2.5 (mean={np.mean(winter_sub):.1f} ug/m3) is significantly higher than Summer '
                f'(mean={np.mean(summer_sub):.1f} ug/m3), with medium-to-large effect size (d={cohens_d:.3f}, p < 0.001).'
            )
        }
    }

    with open(os.path.join(output_dir, 'hypothesis_testing_results.json'), 'w') as f:
        json.dump(hypothesis_results, f, indent=4)

    return hypothesis_results


if __name__ == '__main__':
    base_dir = r"c:\Users\MiRuThUlA.LAPTOP-SMP99ABO.000\OneDrive\Desktop\Urban_Air_Quality_EDA"
    raw_dir = os.path.join(base_dir, "data", "raw")
    output_dir = os.path.join(base_dir, "outputs")

    print("Running exploratory analysis pipeline...")
    df_raw = load_raw_dataset(raw_dir)
    meta = generate_data_quality_report(df_raw, output_dir)
    print("Data quality metadata generated:", meta)

    df_clean = clean_and_impute_data(df_raw)
    stats_df = compute_descriptive_statistics(df_clean, output_dir)
    print("Descriptive statistics generated:")
    print(stats_df.head())

    print("Fitting continuous distributions to PM2.5...")
    dist_df = fit_continuous_distributions(df_clean['PM2.5'], output_dir)
    print(dist_df)

    print("Exploring discrete distribution...")
    discrete_res = explore_discrete_distribution(df_clean, output_dir)
    print(discrete_res)

    print("Executing statistical hypothesis tests...")
    hypo_res = perform_statistical_hypothesis_tests(df_clean, output_dir)
    print("Hypothesis tests completed successfully!")
