# Beijing Multi-Site Air Quality Dataset

## Source & Attribution
- **Dataset Title:** Beijing Multi-Site Air Quality Data
- **Repository:** UCI Machine Learning Repository
- **URL:** https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data
- **DOI:** https://doi.org/10.24432/C5K306
- **Creators:** Song Chen (Tsinghua University)
- **Time Coverage:** March 1, 2013 to February 28, 2017 (Hourly resolution, 1,461 days, 35,064 hourly timestamps per station)
- **Spatial Coverage:** 12 nationally-controlled air quality monitoring sites in Beijing, China:
  1. Aotizhongxin (Olympic Sports Center)
  2. Changping
  3. Dingling
  4. Dongsi
  5. Guanyuan
  6. Gucheng
  7. Huairou
  8. Nongzhanguan (Agricultural Exhibition Hall)
  9. Shunyi
  10. Tiantan (Temple of Heaven)
  11. Wanliu
  12. Wanshouxigong

## Total Dimensions
- **Number of Stations:** 12
- **Records per Station:** 35,064
- **Total Combined Observations:** 420,768 records
- **Number of Attributes:** 18 features

## Attributes & Field Definitions
| # | Field Name | Type | Unit | Description |
|---|---|---|---|---|
| 1 | `No` | Integer | Dimensionless | Record identification number |
| 2 | `year` | Integer | Year (YYYY) | Observation year (2013 - 2017) |
| 3 | `month` | Integer | Month (1-12) | Observation month |
| 4 | `day` | Integer | Day (1-31) | Observation day |
| 5 | `hour` | Integer | Hour (0-23) | Observation hour in local time |
| 6 | `PM2.5` | Float | $\mu g / m^3$ | Fine particulate matter concentration with aerodynamic diameter $\le 2.5\mu m$ |
| 7 | `PM10` | Float | $\mu g / m^3$ | Inhalable particulate matter concentration with aerodynamic diameter $\le 10\mu m$ |
| 8 | `SO2` | Float | $\mu g / m^3$ | Sulfur dioxide concentration |
| 9 | `NO2` | Float | $\mu g / m^3$ | Nitrogen dioxide concentration |
| 10 | `CO` | Float | $\mu g / m^3$ | Carbon monoxide concentration |
| 11 | `O3` | Float | $\mu g / m^3$ | Ground-level ozone concentration |
| 12 | `TEMP` | Float | $^\circ C$ | Ambient surface temperature |
| 13 | `PRES` | Float | $hPa$ | Atmospheric pressure |
| 14 | `DEWP` | Float | $^\circ C$ | Dew point temperature |
| 15 | `RAIN` | Float | $mm$ | Hourly cumulative precipitation |
| 16 | `wd` | Categorical | Cardinal/ordinal | 16-point compass wind direction (N, NNE, NE, ..., WNW, NW, NNW, cv) |
| 17 | `WSPM` | Float | $m / s$ | Surface wind speed |
| 18 | `station` | Categorical | String | Monitoring station location identifier |

## Preprocessing & Data Cleaning Protocol
1. **Timestamp Assembly:** `year`, `month`, `day`, `hour` are converted into an explicit ISO-8601 Datetime index `timestamp` spanning `2013-03-01 00:00:00` to `2017-02-28 23:00:00`.
2. **Missing Values:**
   - Continuous pollutant and meteorological series feature small missing gaps due to sensor recalibration or brief outages.
   - Forward-backward linear interpolation is applied within each station's continuous timeline to preserve autocorrelation structures.
   - Categorical wind direction (`wd`) is imputed using forward fill / modal category.
3. **Outliers:** Physical limits are verified. Realistic extreme pollution episodes (e.g., severe winter haze with $PM2.5 > 500\mu g/m^3$) are preserved because they reflect genuine atmospheric hazards, while impossible negative readings are clipped.
4. **Time-Aware Train-Validation-Test Split:**
   - Training: `2013-03-01 00:00:00` to `2016-02-29 23:00:00` (36 months, ~75%)
   - Validation: `2016-03-01 00:00:00` to `2016-10-31 23:00:00` (8 months, ~17%)
   - Testing: `2016-11-01 00:00:00` to `2017-02-28 23:00:00` (4 months, ~8%, held-out winter forecasting test set)
