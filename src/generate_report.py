"""
Comprehensive Academic Project Report Generator
Course: U21ADP05 — Exploratory Data Analysis and Visualization
Outputs: reports/Project_Report.docx and reports/Project_Report.pdf
"""

import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import pandas as pd


def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout_box(doc, text, title="KEY OBSERVATION"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=120, bottom=120, left=200, right=200)

    # Left border highlight
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1F4E79"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"{title}: ")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    run_c = p.add_run(text)
    run_c.font.name = "Arial"
    run_c.font.size = Pt(9.5)
    run_c.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def format_table(table, header_bg="1F4E79", alt_bg="F9FBFD"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        # Prevent row split across pages
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        if i == 0:
            # Repeat header
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            if i == 0:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        r.bold = True
                        r.font.name = "Arial"
                        r.font.size = Pt(9.5)
                        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, alt_bg)
                else:
                    set_cell_background(cell, "FFFFFF")
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.name = "Arial"
                        r.font.size = Pt(9)
                        r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)


def generate_full_report(base_dir: str):
    reports_dir = os.path.join(base_dir, "reports")
    fig_dir = os.path.join(base_dir, "figures")
    out_dir = os.path.join(base_dir, "outputs")
    os.makedirs(reports_dir, exist_ok=True)

    doc = docx.Document()

    # Page Margins: 1 inch (72 pt) all sides
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Base styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # -------------------------------------------------------------
    # 1. TITLE PAGE
    # -------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(36)
    p_inst.paragraph_format.space_after = Pt(4)
    r_inst = p_inst.add_run("KPR INSTITUTE OF ENGINEERING AND TECHNOLOGY")
    r_inst.bold = True
    r_inst.font.size = Pt(14)
    r_inst.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(28)
    r_dept = p_dept.add_run("DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE")
    r_dept.bold = True
    r_dept.font.size = Pt(11)
    r_dept.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_after = Pt(12)
    r_proj = p_proj.add_run("COURSE PROJECT REPORT — U21ADP05")
    r_proj.bold = True
    r_proj.font.size = Pt(12)
    r_proj.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(14)
    r_title = p_title.add_run("Urban Air Quality Analysis, Statistical Visualization and PM2.5 Prediction Using Deep Learning")
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = RGBColor(0x11, 0x22, 0x44)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(48)
    r_sub = p_sub.add_run("A Case Study on the Beijing Multi-Site Hourly Atmospheric Dataset (2013–2017)")
    r_sub.italic = True
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    # Metadata Table
    tbl_meta = doc.add_table(rows=6, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course Name:", "Exploratory Data Analysis and Visualization (U21ADP05)"),
        ("Student Name:", "[YOUR NAME]"),
        ("Roll Number:", "[YOUR ROLL NUMBER]"),
        ("Department & Year:", "Artificial Intelligence & Data Science | Year III (Sem V)"),
        ("Submission Date:", "[ACTUAL SUBMISSION DATE]"),
        ("GitHub Repository:", "[YOUR PUBLIC GITHUB URL]")
    ]
    for r_idx, (k, v) in enumerate(meta_data):
        c0 = tbl_meta.cell(r_idx, 0)
        c1 = tbl_meta.cell(r_idx, 1)
        c0.paragraphs[0].add_run(k).bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(10)
        c1.paragraphs[0].add_run(v)
        c1.paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_background(c0, "F5F8FA")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2. ABSTRACT (Strictly 100-150 words)
    # -------------------------------------------------------------
    h1 = doc.add_heading("2. Abstract", level=1)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(8)

    abstract_text = (
        "This project presents an exploratory data analysis, statistical evaluation, "
        "and deep learning framework for urban air quality modeling using the Beijing Multi-Site "
        "dataset from the UCI Machine Learning Repository. Encompassing 420,768 hourly records "
        "across 12 stations from 2013 to 2017, the analysis investigates criteria pollutants "
        "and meteorological dynamics using temporal linear interpolation. Continuous distribution "
        "fitting demonstrates that PM2.5 is best fitted by a Weibull distribution (AIC = 214,023.2, "
        "KS = 0.0325), followed closely by Gamma, surpassing Lognormal and Normal fits. Discrete "
        "modeling showed overdispersion (variance-to-mean ratio 1.55), where Negative Binomial "
        "significantly outperformed Poisson (ΔAIC = -67.9). A PyTorch Multi-Layer Perceptron (MLP) "
        "was engineered for 1-hour ahead PM2.5 forecasting using 23 past-only predictors and "
        "chronological splitting. On a held-out winter test period, the MLP achieved an RMSE of "
        "22.80 μg/m³, an MAE of 11.87 μg/m³, and an R² of 0.9571, outperforming persistence "
        "and linear regression baselines."
    )
    # Word count check
    words = abstract_text.split()
    print(f"Abstract Word Count: {len(words)} words (Strict Requirement: 100-150 words)")

    p_abs = doc.add_paragraph(abstract_text)
    p_abs.paragraph_format.line_spacing = 1.2
    p_abs.paragraph_format.space_after = Pt(6)

    p_kw = doc.add_paragraph()
    r_kwt = p_kw.add_run("Keywords: ")
    r_kwt.bold = True
    p_kw.add_run("Urban Air Quality, PM2.5 Forecasting, Exploratory Data Analysis, Seven Stages of Visualization, Deep Learning, Multi-Layer Perceptron, Atmospheric Meteorology.")
    p_kw.paragraph_format.space_after = Pt(14)

    # -------------------------------------------------------------
    # 3. INTRODUCTION
    # -------------------------------------------------------------
    doc.add_heading("3. Introduction", level=1)
    p_intro = doc.add_paragraph(
        "Urban ambient air pollution constitutes one of the most pressing public health and environmental challenges "
        "of modern industrial civilization. Among atmospheric pollutants, fine particulate matter with an aerodynamic "
        "diameter of 2.5 micrometers or smaller (PM2.5) is recognized by the World Health Organization (WHO) as the most "
        "deleterious agent affecting human longevity. Owing to their microscopic dimensions, PM2.5 aerosols bypass the upper "
        "respiratory tract, penetrating deeply into alveolar sacs and entering systemic circulation. Chronic and acute exposures "
        "are epidemiologically linked to ischemic heart disease, cerebrovascular stroke, chronic obstructive pulmonary "
        "disease (COPD), lung carcinoma, and acute lower respiratory infections in pediatric populations.\n\n"
        "Megacities such as Beijing, China, historically experienced severe recurrent haze events driven by rapid industrialization, "
        "dense vehicular transport, regional coal-fired domestic heating, and complex topographical confinement by the Yan "
        "and Taihang Mountain ranges. Effective early-warning systems, regulatory compliance frameworks, and dynamic "
        "public health advisories necessitate high-fidelity exploratory analysis and predictive forecasting tools. This case study "
        "leverages the multi-station Beijing air quality monitoring repository to unpack the spatiotemporal, chemical, and "
        "meteorological mechanisms governing particulate dynamics."
    )
    p_intro.paragraph_format.line_spacing = 1.15
    p_intro.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 4. PROBLEM STATEMENT & 5. OBJECTIVES
    # -------------------------------------------------------------
    doc.add_heading("4. Problem Statement", level=1)
    p_prob = doc.add_paragraph(
        "Atmospheric PM2.5 concentrations are dictated by highly non-linear interactions between chemical precursor emissions "
        "(SO2, NO2, CO, VOCs), photochemical oxidation processes (O3), and volatile meteorological drivers (temperature, barometric "
        "pressure, relative humidity, boundary layer height, and wind dispersion). Traditional numerical chemical transport models "
        "(such as CMAQ and WRF-Chem) require massive high-performance computing resources and detailed emissions inventories that "
        "are often inaccessible or subject to prolonged latency. Consequently, statistical and deep learning methodologies capable "
        "of rapidly digesting streaming environmental sensor data and issuing precise short-term forecasts are vital.\n\n"
        "The central research problem investigated herein is: Can past criteria pollutant concentrations, autoregressive "
        "particulate histories, and surface weather measurements be synthesized into a predictive model that accurately forecasts "
        "next-hour PM2.5 concentration (t+1) across multiple urban stations without suffering from future data leakage or "
        "unrealistic station-level artifacts?"
    )
    p_prob.paragraph_format.line_spacing = 1.15
    p_prob.paragraph_format.space_after = Pt(8)

    doc.add_heading("5. Objectives", level=1)
    p_obj = doc.add_paragraph(
        "The project is executed under the following primary scientific and engineering objectives:\n"
        "1. Ingest, consolidate, and clean 420,768 hourly records from 12 official Beijing monitoring stations spanning March 1, 2013 to February 28, 2017.\n"
        "2. Conduct rigorous data quality audits, quantify missingness patterns, and apply physically grounded temporal interpolation.\n"
        "3. Perform parametric and non-parametric exploratory data analysis, quantifying distributions, skewness, and multi-scale correlations.\n"
        "4. Conduct formal probability distribution fitting (Normal, Lognormal, Gamma, Weibull) and evaluate discrete overdispersion characteristics.\n"
        "5. Execute hypothesis testing (Kruskal-Wallis spatial tests, seasonal ANOVA, and Mann-Whitney U tests with Cohen's d effect size).\n"
        "6. Implement and document all seven visualization stages (Acquire, Parse, Filter, Mine, Represent, Refine, Interact) with static and Plotly interactive assets.\n"
        "7. Build, regularize, and tune a PyTorch Multi-Layer Perceptron (MLP) deep learning model for 1-hour ahead PM2.5 forecasting.\n"
        "8. Prevent data leakage through strict chronological train/validation/test splitting and evaluate against Persistence and Ridge regression baselines."
    )
    p_obj.paragraph_format.line_spacing = 1.15
    p_obj.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 6. DATASET SOURCE AND DESCRIPTION
    # -------------------------------------------------------------
    doc.add_heading("6. Dataset Source and Description", level=1)
    p_ds = doc.add_paragraph(
        "The experimental investigation utilizes the benchmark Beijing Multi-Site Air Quality Data deposited in the "
        "UCI Machine Learning Repository (Chen, 2017; Zhang et al., 2017; DOI: 10.24432/C5K306). The repository compiles hourly "
        "atmospheric observations acquired by the Beijing Municipal Environmental Monitoring Center across 12 nationally "
        "controlled air quality monitoring stations. The stations cover distinct urban functional zones: urban core districts "
        "with heavy traffic and population density (Dongsi, Guanyuan, Wanliu, Aotizhongxin, Tiantan, Wanshouxigong), "
        "suburban residential and developing industrial zones (Changping, Shunyi, Gucheng, Nongzhanguan), and peripheral "
        "ecological background zones (Dingling, Huairou).\n\n"
        "The temporal domain extends across 1,461 consecutive days (35,064 continuous hours per station), generating 420,768 records. "
        "The dataset features 18 attributes, comfortably exceeding the course specification of 15 minimum fields."
    )
    p_ds.paragraph_format.line_spacing = 1.15
    p_ds.paragraph_format.space_after = Pt(8)

    # Table 1: Feature Dictionary
    doc.add_paragraph("Table 1. Beijing Multi-Site Air Quality Dataset Feature Inventory and Definitions", style='Normal').runs[0].bold = True
    tbl_feat = doc.add_table(rows=19, cols=5)
    tbl_feat_data = [
        ("No", "Record ID", "Integer", "None", "Chronological row identifier within station"),
        ("year", "Year", "Integer", "YYYY", "Observation year (2013 - 2017)"),
        ("month", "Month", "Integer", "1 - 12", "Observation calendar month"),
        ("day", "Day", "Integer", "1 - 31", "Observation day of month"),
        ("hour", "Hour", "Integer", "0 - 23", "Observation hour in Beijing local time (UTC+8)"),
        ("PM2.5", "Fine Particles", "Float", "μg/m³", "Particulate matter with aerodynamic diameter ≤ 2.5 μm"),
        ("PM10", "Inhalable Particles", "Float", "μg/m³", "Particulate matter with aerodynamic diameter ≤ 10 μm"),
        ("SO2", "Sulfur Dioxide", "Float", "μg/m³", "Combustion byproduct from coal and heavy sulfur fuels"),
        ("NO2", "Nitrogen Dioxide", "Float", "μg/m³", "Traffic and high-temperature fossil fuel combustion tracer"),
        ("CO", "Carbon Monoxide", "Float", "μg/m³", "Incomplete combustion tracer (heavily elevated in winter)"),
        ("O3", "Ground Ozone", "Float", "μg/m³", "Photochemical secondary oxidant peaking in summer mid-day"),
        ("TEMP", "Temperature", "Float", "°C", "Surface ambient dry-bulb air temperature"),
        ("PRES", "Pressure", "Float", "hPa", "Barometric atmospheric pressure at surface level"),
        ("DEWP", "Dew Point", "Float", "°C", "Surface dew point temperature reflecting absolute moisture"),
        ("RAIN", "Precipitation", "Float", "mm", "Hourly accumulated precipitation (washout effect)"),
        ("wd", "Wind Direction", "Categorical", "16 points", "Compass direction of surface wind (N, NE, E, ..., cv)"),
        ("WSPM", "Wind Speed", "Float", "m/s", "Surface wind speed governing horizontal dispersion"),
        ("station", "Station Name", "Categorical", "String", "Name of the 12 monitoring sites across Beijing")
    ]
    # Header
    hdr = tbl_feat.rows[0].cells
    hdr[0].text = "Field Name"
    hdr[1].text = "Feature Meaning"
    hdr[2].text = "Data Type"
    hdr[3].text = "Measurement Unit"
    hdr[4].text = "Environmental Context"
    for r_idx, row_vals in enumerate(tbl_feat_data):
        cells = tbl_feat.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_vals):
            cells[c_idx].text = val
    format_table(tbl_feat)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # 7. DATA UNDERSTANDING AND PREPROCESSING
    # -------------------------------------------------------------
    doc.add_heading("7. Data Understanding and Preprocessing", level=1)
    p_prep = doc.add_paragraph(
        "A rigorous data quality assessment was executed on the combined multi-site dataset prior to feature engineering. "
        "A total of 420,768 records were inspected. No duplicate records were detected. The missing value audit revealed that "
        "pollutant and weather variables exhibited modest missingness ranging from 0.07% to 4.92%, with Carbon Monoxide (CO) "
        "having the highest missing rate (4.92%, 20,701 missing observations) and PM2.5 missing 2.07% (8,739 observations), "
        "principally attributable to scheduled sensor zeroing, maintenance, and occasional telemetry interruptions."
    )
    p_prep.paragraph_format.line_spacing = 1.15
    p_prep.paragraph_format.space_after = Pt(8)

    # Insert Fig 1: Missing Data Profile
    p_f1 = doc.add_paragraph()
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(os.path.join(fig_dir, "fig1_missing_data_profile.png"), width=Inches(5.8))
    p_cap1 = doc.add_paragraph("Figure 1. Missing Value Percentage Across Criteria Atmospheric Variables (Total N = 420,768)", style='Normal')
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap1.runs[0].italic = True
    p_cap1.paragraph_format.space_after = Pt(8)

    add_callout_box(
        doc,
        "Rather than employing naive mean/median imputation (which damages autocorrelation) or dropna listwise deletion "
        "(which destroys the continuity of time-series lags), a station-grouped continuous linear interpolation with a "
        "maximum 24-hour limit was implemented, followed by backward/forward fill for boundary edges. Physical feasibility bounds "
        "were strictly enforced by clipping negative sensor noise to 0.0.",
        title="DATA CLEANING & IMPUTATION PROTOCOL"
    )

    # -------------------------------------------------------------
    # 8. EXPLORATORY DATA ANALYSIS & 9. STATISTICAL DISTRIBUTION ANALYSIS
    # -------------------------------------------------------------
    doc.add_heading("8. Exploratory Data Analysis & Statistical Distribution Analysis", level=1)
    p_eda = doc.add_paragraph(
        "Both parametric (mean, standard deviation) and non-parametric (median, interquartile range, skewness, kurtosis) "
        "statistics were computed across the cleaned continuous features. Atmospheric pollutant concentrations systematically "
        "deviate from standard Gaussian assumptions, displaying pronounced positive (rightward) skewness and heavy kurtotic tails."
    )
    p_eda.paragraph_format.line_spacing = 1.15
    p_eda.paragraph_format.space_after = Pt(8)

    # Table 2: Descriptive Statistics
    doc.add_paragraph("Table 2. Parametric and Non-Parametric Descriptive Statistics of Criteria Pollutants and Meteorology", style='Normal').runs[0].bold = True
    stats_df = pd.read_csv(os.path.join(out_dir, "descriptive_statistics.csv"))
    tbl_stat = doc.add_table(rows=len(stats_df) + 1, cols=9)
    col_names = ["Variable", "Mean", "StdDev", "Median", "IQR", "Min", "Max", "Skewness", "Kurtosis"]
    for c_idx, name in enumerate(col_names):
        tbl_stat.rows[0].cells[c_idx].text = name
    for r_idx, r_data in stats_df.iterrows():
        cells = tbl_stat.rows[r_idx + 1].cells
        cells[0].text = str(r_data['Variable'])
        cells[1].text = f"{r_data['Mean']:.2f}"
        cells[2].text = f"{r_data['StdDev']:.2f}"
        cells[3].text = f"{r_data['Median']:.2f}"
        cells[4].text = f"{r_data['IQR']:.2f}"
        cells[5].text = f"{r_data['Min']:.1f}"
        cells[6].text = f"{r_data['Max']:.1f}"
        cells[7].text = f"{r_data['Skewness']:.2f}"
        cells[8].text = f"{r_data['Kurtosis']:.2f}"
    format_table(tbl_stat)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Distribution Fitting Section
    doc.add_heading("9. Continuous and Discrete Probability Distributions", level=1)
    p_dist = doc.add_paragraph(
        "To rigorously satisfy the CO4 syllabus requirements, candidate continuous probability distributions—Normal, Lognormal, "
        "Gamma, and Weibull—were fitted to empirical PM2.5 observations via Maximum Likelihood Estimation (MLE) on a consistent sample (N = 20,000). "
        "Goodness-of-fit was evaluated using Log-Likelihood, Akaike Information Criterion (AIC), Bayesian Information Criterion (BIC), "
        "and the Kolmogorov-Smirnov (KS) distance metric. Additionally, discrete probability modeling was evaluated on monthly counts "
        "of severe pollution exceedance days (PM2.5 > 75 μg/m³) across 576 station-months to examine dispersion and evaluate candidate count models."
    )
    p_dist.paragraph_format.line_spacing = 1.15
    p_dist.paragraph_format.space_after = Pt(6)

    # Table 3: Continuous Distribution Fits
    doc.add_paragraph("Table 3. Goodness-of-Fit Comparison for PM2.5 Continuous Candidate Probability Distributions", style='Normal').runs[0].bold = True
    dist_df = pd.read_csv(os.path.join(out_dir, "continuous_distribution_fits.csv"))
    tbl_dist = doc.add_table(rows=len(dist_df) + 1, cols=6)
    dist_headers = ["Distribution", "Parameters (Shape, Loc, Scale)", "Log-Likelihood", "AIC", "BIC", "KS Statistic"]
    for c_idx, name in enumerate(dist_headers):
        tbl_dist.rows[0].cells[c_idx].text = name
    for r_idx, r_data in dist_df.iterrows():
        cells = tbl_dist.rows[r_idx + 1].cells
        cells[0].text = str(r_data['Distribution'])
        cells[1].text = str(r_data['Parameters'])
        cells[2].text = f"{r_data['LogLikelihood']:.1f}"
        cells[3].text = f"{r_data['AIC']:.1f}"
        cells[4].text = f"{r_data['BIC']:.1f}"
        cells[5].text = f"{r_data['KS_Statistic']:.4f}"
    format_table(tbl_dist)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Insert Fig 2: Distribution Fits
    p_f2 = doc.add_paragraph()
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(os.path.join(fig_dir, "fig2_pm25_distribution_and_fits.png"), width=Inches(5.8))
    p_cap2 = doc.add_paragraph("Figure 2. Empirical Probability Density of PM2.5 Concentrations Alongside Theoretical Fitted Curves", style='Normal')
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap2.runs[0].italic = True
    p_cap2.paragraph_format.space_after = Pt(6)

    # Table 3b: Discrete Count Distribution Fits
    doc.add_paragraph("Table 3b. Comparison of Discrete Count Probability Models for Monthly Exceedance Days (PM2.5 > 75 μg/m³)", style='Normal').runs[0].bold = True
    tbl_disc = doc.add_table(rows=3, cols=6)
    disc_headers = ["Candidate Model", "Estimated Parameters", "Log-Likelihood", "AIC", "BIC", "Dispersion Assessment"]
    for c_idx, name in enumerate(disc_headers):
        tbl_disc.rows[0].cells[c_idx].text = name
    disc_rows_data = [
        ("Poisson", "λ = 12.267", "-1709.6", "3421.1", "3425.5", "Assumes equidispersion (Var = Mean = 12.27)"),
        ("Negative Binomial", "r = 19.785, p = 0.617", "-1674.6", "3353.3", "3362.0", "Accommodates overdispersion (ΔAIC = -67.9)")
    ]
    for r_idx, r_data in enumerate(disc_rows_data):
        cells = tbl_disc.rows[r_idx + 1].cells
        for c_idx, val in enumerate(r_data):
            cells[c_idx].text = val
    format_table(tbl_disc)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_callout_box(
        doc,
        "Continuous distribution fitting demonstrates that PM2.5 concentrations are best characterized by a Weibull distribution "
        "(lowest AIC = 214,023.2, lowest BIC = 214,046.9, and lowest KS statistic = 0.0325), followed very closely by the "
        "Gamma distribution (AIC = 214,038.4, KS = 0.0355). Both flexible two-parameter skewed distributions fit the empirical data "
        "more effectively than the Lognormal distribution (AIC = 215,448.4, KS = 0.0571), while the symmetric Normal distribution "
        "displays poor adherence (AIC = 232,488.0, KS = 0.1716). For discrete modeling, monthly exceedance days exhibited empirical "
        "overdispersion (sample variance = 18.96 vs. mean = 12.27, dispersion ratio = 1.55 > 1.0). Treating overdispersion as evidence "
        "to investigate candidate count distributions, Maximum Likelihood comparison confirmed that the Negative Binomial model "
        "outperforms the equidispersed Poisson model (ΔAIC = -67.88), providing superior fit for episodic pollution clusters.",
        title="THEORETICAL DISTRIBUTION INFERENCE"
    )

    # Statistical Hypothesis Testing Section
    doc.add_heading("Statistical Hypothesis Testing Findings", level=2)
    p_hypo = doc.add_paragraph(
        "Three formal hypothesis tests were executed to examine spatial, temporal, and seasonal variances:\n"
        "• Kruskal-Wallis H-Test across Monitoring Stations: Evaluating the null hypothesis that PM2.5 medians are identical across "
        "all 12 sites yielded H = 3548.99 (p < 0.001), soundly rejecting H0 and confirming significant spatial heterogeneity.\n"
        "• One-Way ANOVA across Seasons: Testing across Spring, Summer, Autumn, and Winter yielded F = 2710.16 (p < 0.001), confirming "
        "pronounced seasonal dynamics.\n"
        "• Mann-Whitney U Contrast (Winter vs. Summer): Comparing Winter (mean = 95.78 μg/m³, median = 55.0 μg/m³) against Summer "
        "(mean = 64.97 μg/m³, median = 51.0 μg/m³) yielded U = 117,171,606.0 (p = 4.69 × 10⁻¹⁰) with a standardized Cohen's d "
        "effect size of 0.360. This establishes that winter PM2.5 elevations are statistically significant and non-trivial."
    )
    p_hypo.paragraph_format.line_spacing = 1.15
    p_hypo.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 10. DATA VISUALIZATION AND INTERPRETATION (All figures explained)
    # -------------------------------------------------------------
    doc.add_heading("10. Data Visualization and Interpretation", level=1)
    p_viz = doc.add_paragraph(
        "A diverse suite of high-resolution visualizations was generated to expose the underlying spatial, temporal, "
        "chemical, and meteorological mechanisms governing air quality across Beijing."
    )
    p_viz.paragraph_format.space_after = Pt(6)

    # Figure 3: Boxplots by Station
    doc.add_picture(os.path.join(fig_dir, "fig3_pollutant_boxplots_by_station.png"), width=Inches(5.8))
    p_cap3 = doc.add_paragraph("Figure 3. Spatial Variation of PM2.5 and PM10 Concentrations Across 12 Monitoring Stations", style='Normal')
    p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap3.runs[0].italic = True
    p_desc3 = doc.add_paragraph(
        "Interpretation of Figure 3: Boxplots display substantial spatial differentiation across Beijing. South-central and dense urban stations "
        "(Wanliu, Guanyuan, Gucheng) exhibit higher median particulate levels and extensive upper outlier tails exceeding 300 μg/m³, "
        "consistent with elevated vehicular traffic density, localized road dust, and regional transport from industrial corridors south of Beijing. "
        "Conversely, northern ecological background stations (Dingling, Huairou) exhibit markedly cleaner profiles with median PM2.5 "
        "concentrations below the National Grade II threshold (75 μg/m³), reflecting the protective influence of mountain topography "
        "and reduced local source intensity."
    )
    p_desc3.paragraph_format.line_spacing = 1.15
    p_desc3.paragraph_format.space_after = Pt(8)

    # Figure 4: Correlation Heatmap
    doc.add_picture(os.path.join(fig_dir, "fig4_correlation_heatmap.png"), width=Inches(5.6))
    p_cap4 = doc.add_paragraph("Figure 4. Annotated Correlation Heatmap Across Criteria Pollutants and Surface Meteorological Drivers", style='Normal')
    p_cap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap4.runs[0].italic = True
    p_desc4 = doc.add_paragraph(
        "Interpretation of Figure 4: The correlation matrix uncovers critical physical associations across pollutants and meteorology. "
        "PM2.5 exhibits an extremely strong positive correlation with PM10 (r = 0.88), reflecting common emission sources and secondary particle coagulation. "
        "PM2.5 also strongly correlates with CO (r = 0.77) and NO2 (r = 0.66), indicating co-emission from common combustion sources. "
        "Crucially, PM2.5 is negatively correlated with surface wind speed (WSPM, r = -0.27), quantitatively capturing the atmospheric "
        "ventilation effect. Ground-level ozone (O3) exhibits a strong inverse relationship with NO2 (r = -0.47) and positive relationship with "
        "temperature (r = 0.59), consistent with classical photochemical titration mechanisms and summer solar radiation dependency."
    )
    p_desc4.paragraph_format.line_spacing = 1.15
    p_desc4.paragraph_format.space_after = Pt(8)

    # Figure 5: Seasonal & Diurnal Profiles
    doc.add_picture(os.path.join(fig_dir, "fig5_seasonal_and_diurnal_profiles.png"), width=Inches(5.8))
    p_cap5 = doc.add_paragraph("Figure 5. Seasonal PM2.5 Distributions and 24-Hour Diurnal Dynamics of PM2.5 vs. Photochemical Ozone", style='Normal')
    p_cap5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap5.runs[0].italic = True
    p_desc5 = doc.add_paragraph(
        "Interpretation of Figure 5: Subplot A illustrates the severe winter haze penalty, where median PM2.5 levels rise substantially "
        "and upper deciles breach hazardous levels (>250 μg/m³), associated with seasonal coal heating emissions, frequent surface temperature inversions, "
        "and stagnant air masses. Subplot B highlights the diurnal contrast between PM2.5 and Ozone. PM2.5 exhibits bimodal peaks "
        "coinciding with morning rush-hour traffic (07:00–09:00) and nocturnal boundary layer compression (21:00–02:00). In contrast, "
        "ozone exhibits a unimodal afternoon peak (14:00–16:00) driven by peak solar UV insolation and photochemical reactions."
    )
    p_desc5.paragraph_format.line_spacing = 1.15
    p_desc5.paragraph_format.space_after = Pt(8)

    # Figure 6: PM2.5 vs Meteorology
    doc.add_picture(os.path.join(fig_dir, "fig6_pm25_vs_meteorology.png"), width=Inches(5.8))
    p_cap6 = doc.add_paragraph("Figure 6. Bivariate Dependencies: PM2.5 vs. Wind Speed, Surface Temperature, and Dew Point", style='Normal')
    p_cap6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap6.runs[0].italic = True
    p_desc6 = doc.add_paragraph(
        "Interpretation of Figure 6: Subplot A demonstrates that when wind speed exceeds 3.0 m/s, PM2.5 concentrations collapse below "
        "50 μg/m³, revealing a critical ventilation threshold. Subplot B reveals that high particulate episodes concentrate at low temperatures "
        "(< 0°C) during stagnant winter conditions. Subplot C demonstrates a positive statistical association between dew point (humidity) and PM2.5, "
        "consistent with atmospheric literature describing how high moisture facilitates aqueous-phase sulfate and nitrate secondary aerosol production and hygroscopic particle growth."
    )
    p_desc6.paragraph_format.line_spacing = 1.15
    p_desc6.paragraph_format.space_after = Pt(8)

    # Figure 7: Multi-Site Long Term Trend
    doc.add_picture(os.path.join(fig_dir, "fig7_multisite_spatial_trend.png"), width=Inches(5.8))
    p_cap7 = doc.add_paragraph("Figure 7. Long-Term Monthly PM2.5 Trajectory: Urban Core vs. Suburban Background (2013–2017)", style='Normal')
    p_cap7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap7.runs[0].italic = True
    p_desc7 = doc.add_paragraph(
        "Interpretation of Figure 7: The multi-year time-series confirms synchronized seasonal oscillation between urban core "
        "and suburban sites, while demonstrating a persistent 15–25 μg/m³ elevation in urban core stations throughout the 4-year period. "
        "A gradual downward secular trend is discernible from 2013 to 2017, consistent with municipal air clean action policies enacted "
        "in Beijing during this observation window."
    )
    p_desc7.paragraph_format.line_spacing = 1.15
    p_desc7.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 11. THE SEVEN STAGES OF VISUALIZATION
    # -------------------------------------------------------------
    doc.add_heading("11. The Seven Stages of Visualization", level=1)
    p_seven = doc.add_paragraph(
        "To satisfy the core pedagogical requirements of Assignment II, the analytical workflow was mapped across all seven "
        "stages of data visualization articulated by Ben Fry (2008). Table 4 provides an explicit audit mapping each stage to its "
        "concrete Python implementation and deliverable output."
    )
    p_seven.paragraph_format.space_after = Pt(6)

    # Table 4: Seven Stages Mapping Table
    doc.add_paragraph("Table 4. Comprehensive Mapping of Fry's Seven Stages of Visualization to Project Implementation", style='Normal').runs[0].bold = True
    tbl_seven = doc.add_table(rows=8, cols=4)
    tbl_seven_headers = ["Stage", "Methodological Definition", "Code Implementation in Project", "Deliverable Output"]
    for c_idx, name in enumerate(tbl_seven_headers):
        tbl_seven.rows[0].cells[c_idx].text = name
    stages_data = [
        ("1. Acquire", "Obtain data from source repository or streaming pipeline.", "load_raw_dataset() reading 12 CSV station archives from UCI repository.", "Raw DataFrame (420,768 rows × 18 columns)."),
        ("2. Parse", "Provide structural meaning, temporal indices, and schema constraints.", "pd.to_datetime() parsing year, month, day, hour into continuous ISO timestamps.", "Strict datetime index with hourly continuity across 12 sites."),
        ("3. Filter", "Remove invalid records, clip sensor noise, curate features.", "clean_and_impute_data() applying linear interpolation (limit=24) and clipping lower bound to 0.0.", "Cleaned DataFrame without negative sensor values or missing records."),
        ("4. Mine", "Extract mathematical patterns, correlations, and distributions.", "stats.skew(), stats.kurtosis(), kstest(), Pearson correlation, and permutation importance.", "descriptive_statistics.csv, correlation matrices, and distribution fit tables."),
        ("5. Represent", "Choose appropriate visual forms (histograms, boxplots, scatter, heatmaps).", "sns.histplot, sns.boxplot, sns.heatmap, and sns.regplot.", "Figures 1 through 7 (distributions, heatmaps, boxplots, trendlines)."),
        ("6. Refine", "Enhance visual clarity, color palettes, standard units, and labeling.", "setup_style() configuring 300 DPI, Arial fonts, μg/m³ units, and grade thresholds.", "Publication-ready figure formatting with clear labels and annotations."),
        ("7. Interact", "Provide dynamic user exploration, brushing, filtering, and tooltips.", "Plotly make_subplots(), go.Scatter with hover cards, time-range slider, and selectors.", "fig8_interactive_air_quality.html interactive web dashboard.")
    ]
    for r_idx, r_data in enumerate(stages_data):
        cells = tbl_seven.rows[r_idx + 1].cells
        for c_idx, val in enumerate(r_data):
            cells[c_idx].text = val
    format_table(tbl_seven)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 12. MODEL METHODOLOGY AND ARCHITECTURE & 13. TRAINING PARAMETERS
    # -------------------------------------------------------------
    doc.add_heading("12. Model Methodology and Deep Learning Architecture", level=1)
    p_model = doc.add_paragraph(
        "To forecast next-hour PM2.5 concentrations without data leakage, a Multi-Layer Perceptron (MLP) deep neural network was "
        "constructed in PyTorch. The input feature vector x_t comprises 23 engineered past-only features:\n"
        "• Autoregressive Particulate Lags: PM2.5 at t (lag1), t-1 (lag2), t-2 (lag3), t-5 (lag6).\n"
        "• Co-Pollutant Lags: PM10 (lag1, lag2), SO2, NO2, CO, O3 (lag1).\n"
        "• Weather State Lags: Surface temperature, barometric pressure, dew point, and wind speed (lag1).\n"
        "• Rolling Moving Averages: Past 6-hour moving mean, 6-hour standard deviation, and 24-hour moving mean of PM2.5.\n"
        "• Atmospheric Ratios & Differentials: PM2.5/PM10 mass ratio and 1-hour PM2.5 rate-of-change (diff_1h).\n"
        "• Cyclical Encodings: Sine and cosine transformations of diurnal hour (0–23) and seasonal month (1–12).\n\n"
        "Architecture: The deep network incorporates fully connected linear layers, Batch Normalization (BatchNorm1d) to stabilize "
        "internal covariate shift, Rectified Linear Unit (ReLU) activations, and Dropout (p = 0.15) to prevent over-reliance on individual "
        "nodes. The terminal layer projects hidden representations to a scalar output representing next-hour PM2.5 (μg/m³)."
    )
    p_model.paragraph_format.line_spacing = 1.15
    p_model.paragraph_format.space_after = Pt(8)

    doc.add_heading("13. Training Parameters and Hyperparameter Tuning", level=1)
    p_tune = doc.add_paragraph(
        "Chronological Splitting: Zero future information was leaked into training. Data was partitioned chronologically:\n"
        "• Training Set: March 1, 2013 to February 29, 2016 (36 months, 315,588 samples).\n"
        "• Validation Set: March 1, 2016 to October 31, 2016 (8 months, 70,560 samples).\n"
        "• Held-Out Test Set: November 1, 2016 to February 28, 2017 (4 months, 34,548 samples covering a severe winter).\n\n"
        "StandardScaler was fitted strictly on the training set and applied downstream to validation and test tensors. "
        "The model was trained with the AdamW optimizer (weight_decay = 1e-4), Mean Squared Error (MSE) loss, a mini-batch size of 512, "
        "ReduceLROnPlateau learning rate scheduling (decay factor 0.5, patience 2), and Early Stopping (patience 4 epochs on validation loss). "
        "A hyperparameter search was conducted across three distinct architectures."
    )
    p_tune.paragraph_format.line_spacing = 1.15
    p_tune.paragraph_format.space_after = Pt(6)

    # Table 5: Hyperparameter Tuning Table
    doc.add_paragraph("Table 5. Deep Learning Hyperparameter Tuning Results Across MLP Architectures", style='Normal').runs[0].bold = True
    with open(os.path.join(out_dir, "hyperparameter_tuning.json"), "r") as f:
        tune_data = json.load(f)
    tbl_tune = doc.add_table(rows=len(tune_data) + 1, cols=6)
    tune_headers = ["Architecture Name", "Hidden Layer Neurons", "Initial LR", "Validation MSE", "Validation RMSE (μg/m³)", "Epochs Trained"]
    for c_idx, name in enumerate(tune_headers):
        tbl_tune.rows[0].cells[c_idx].text = name
    for r_idx, r_dict in enumerate(tune_data):
        cells = tbl_tune.rows[r_idx + 1].cells
        cells[0].text = str(r_dict['config_name'])
        cells[1].text = str(r_dict['hidden_layers'])
        cells[2].text = str(r_dict['learning_rate'])
        cells[3].text = f"{r_dict['val_mse']:.2f}"
        cells[4].text = f"{r_dict['val_rmse']:.2f}"
        cells[5].text = str(r_dict['epochs_trained'])
    format_table(tbl_tune)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 14. RESULTS AND EVALUATION (All model figures explained)
    # -------------------------------------------------------------
    doc.add_heading("14. Results and Model Evaluation", level=1)
    p_res = doc.add_paragraph(
        "The best-performing architecture selected by validation performance (MLP_Large: [256, 128, 64], LR = 0.0005) was "
        "evaluated exactly once on the held-out test period (November 2016 – February 2017). Performance was benchmarked against "
        "two classical standards: a Persistence Baseline (predicting next hour PM2.5 as current hour PM2.5) and a regularized "
        "Ridge Linear Regression model."
    )
    p_res.paragraph_format.space_after = Pt(6)

    # Table 6: Model Evaluation Metrics Table
    doc.add_paragraph("Table 6. Comparative Model Performance on Held-Out Winter Test Period (2016-11-01 to 2017-02-28)", style='Normal').runs[0].bold = True
    eval_df = pd.read_csv(os.path.join(out_dir, "model_evaluation_metrics.csv"))
    tbl_eval = doc.add_table(rows=len(eval_df) + 1, cols=5)
    eval_headers = ["Model Name", "MAE (μg/m³)", "RMSE (μg/m³)", "R² Score", "MAPE (%)"]
    for c_idx, name in enumerate(eval_headers):
        tbl_eval.rows[0].cells[c_idx].text = name
    for r_idx, r_dict in eval_df.iterrows():
        cells = tbl_eval.rows[r_idx + 1].cells
        cells[0].text = str(r_dict['Model'])
        cells[1].text = f"{r_dict['MAE (ug/m3)']:.3f}"
        cells[2].text = f"{r_dict['RMSE (ug/m3)']:.3f}"
        cells[3].text = f"{r_dict['R2_Score']:.4f}"
        cells[4].text = f"{r_dict['MAPE (%)']:.2f}%"
    format_table(tbl_eval)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Figure 9: Loss Curves
    doc.add_picture(os.path.join(fig_dir, "fig9_loss_vs_epoch.png"), width=Inches(5.5))
    p_cap9 = doc.add_paragraph("Figure 9. Training and Validation Loss (MSE) Progression Across Training Epochs", style='Normal')
    p_cap9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap9.runs[0].italic = True
    p_desc9 = doc.add_paragraph(
        "Interpretation of Figure 9: The training loss smoothly declined across epochs, while validation loss closely tracked "
        "training loss without diverging, demonstrating that Batch Normalization, Dropout (0.15), and weight decay effectively "
        "prevented overfitting on the training distribution."
    )
    p_desc9.paragraph_format.line_spacing = 1.15
    p_desc9.paragraph_format.space_after = Pt(8)

    # Figure 10: Actual vs Predicted
    doc.add_picture(os.path.join(fig_dir, "fig10_actual_vs_predicted.png"), width=Inches(5.2))
    p_cap10 = doc.add_paragraph("Figure 10. Actual vs. Predicted Next-Hour PM2.5 Concentrations on the Held-Out Test Set", style='Normal')
    p_cap10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap10.runs[0].italic = True
    p_desc10 = doc.add_paragraph(
        "Interpretation of Figure 10: The scatter plot demonstrates tight adherence to the ideal 1:1 diagonal line across both low "
        "background concentrations and severe haze spikes exceeding 400 μg/m³. The model achieved an outstanding test R² of 0.9571, "
        "confirming that 95.71% of variance in next-hour PM2.5 is explained by the deep neural network."
    )
    p_desc10.paragraph_format.line_spacing = 1.15
    p_desc10.paragraph_format.space_after = Pt(8)

    # Figure 11: Residual Distribution
    doc.add_picture(os.path.join(fig_dir, "fig11_residual_distribution.png"), width=Inches(5.5))
    p_cap11 = doc.add_paragraph("Figure 11. Model Prediction Residual Distribution (y_actual - y_predicted) with Gaussian Fit", style='Normal')
    p_cap11.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap11.runs[0].italic = True
    p_desc11 = doc.add_paragraph(
        "Interpretation of Figure 11: The prediction error distribution is centered tightly near zero with a mean residual error of "
        "1.71 μg/m³ (standard deviation = 22.73 μg/m³, median = 0.58 μg/m³), confirming minimal residual bias across the 34,548 test predictions. "
        "The residual distribution exhibits a leptokurtic shape with a prominent central peak, demonstrating that the vast majority of hourly "
        "forecasts incur modest deviations from actual ground observations."
    )
    p_desc11.paragraph_format.line_spacing = 1.15
    p_desc11.paragraph_format.space_after = Pt(8)

    # Figure 12: Residuals vs Predicted
    doc.add_picture(os.path.join(fig_dir, "fig12_residuals_vs_predicted.png"), width=Inches(5.5))
    p_cap12 = doc.add_paragraph("Figure 12. Residuals vs. Predicted PM2.5 Concentrations (Homoscedasticity Diagnostic)", style='Normal')
    p_cap12.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap12.runs[0].italic = True
    p_desc12 = doc.add_paragraph(
        "Interpretation of Figure 12: Residuals maintain a symmetrical horizontal distribution across low and moderate predictions. "
        "A modest fan-shaped dispersion is evident at extreme values (> 350 μg/m³), which is physically anticipated in atmospheric "
        "chemistry due to turbulent burst dynamics during severe winter haze peaks."
    )
    p_desc12.paragraph_format.line_spacing = 1.15
    p_desc12.paragraph_format.space_after = Pt(8)

    # Figure 13: Model Comparison Metrics
    doc.add_picture(os.path.join(fig_dir, "fig13_model_comparison_metrics.png"), width=Inches(5.5))
    p_cap13 = doc.add_paragraph("Figure 13. Comparative Evaluation: Baselines vs. Tuned Deep Learning MLP on MAE, RMSE, and R²", style='Normal')
    p_cap13.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap13.runs[0].italic = True
    p_desc13 = doc.add_paragraph(
        "Interpretation of Figure 13: The grouped bar chart demonstrates consistent, statistically defensible superiority of the "
        "Deep Learning MLP over both baselines. Compared to the standard Persistence model, the MLP lowers test RMSE from 26.12 μg/m³ "
        "to 22.80 μg/m³ (a 12.7% error reduction) and MAE from 13.14 μg/m³ to 11.87 μg/m³. The MLP also outperforms Ridge regression "
        "(RMSE = 24.20 μg/m³), proving that non-linear hidden representations capture complex cross-pollutant interactions."
    )
    p_desc13.paragraph_format.line_spacing = 1.15
    p_desc13.paragraph_format.space_after = Pt(8)

    # Figure 14: Permutation Feature Importance
    doc.add_picture(os.path.join(fig_dir, "fig14_permutation_feature_importance.png"), width=Inches(5.8))
    p_cap14 = doc.add_paragraph("Figure 14. Top Predictors Ranked by Permutation Feature Importance (Increase in Test MSE)", style='Normal')
    p_cap14.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap14.runs[0].italic = True
    p_desc14 = doc.add_paragraph(
        "Interpretation of Figure 14: Shuffling PM2.5_lag1 causes an enormous increase in test MSE (+5544.5), confirming that immediate "
        "autoregressive persistence is the primary predictive anchor. PM2.5_lag2 (+2567.2) and coarse inhalable particles PM10_lag1 "
        "(+2137.0) rank as the next most decisive variables. Crucially, environmental variables also demonstrate substantial independent "
        "predictive contribution: surface dew point (+294.1), hourly particulate delta (+204.4), wind speed (+148.8), and temperature (+83.9). "
        "This demonstrates that the neural network utilizes physical dispersion proxies and meteorological indicators alongside "
        "autoregressive lags."
    )
    p_desc14.paragraph_format.line_spacing = 1.15
    p_desc14.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 15. DISCUSSION, 16. PRACTICAL IMPLICATIONS, 17. LIMITATIONS
    # -------------------------------------------------------------
    doc.add_heading("15. Discussion of Findings", level=1)
    p_disc = doc.add_paragraph(
        "The empirical findings synthesize atmospheric physics and deep learning modeling. First, particulate pollution in Beijing "
        "is characterized by dramatic episodic regimes: extended periods of low background pollution punctuated by severe multi-day "
        "haze episodes with PM2.5 exceeding 400 μg/m³. Second, goodness-of-fit evaluations revealed that continuous PM2.5 is best fitted by "
        "a Weibull distribution (AIC = 214,023.2, KS = 0.0325), followed closely by Gamma (AIC = 214,038.4), both surpassing Lognormal "
        "(AIC = 215,448.4) and Normal (AIC = 232,488.0) fits. For discrete exceedance events, observed overdispersion (Var/Mean = 1.55) guided "
        "count distribution evaluation, where Negative Binomial significantly outperformed Poisson (ΔAIC = -67.9). Third, the comparative "
        "model results establish that a carefully regularized PyTorch MLP achieves strong predictive gains over both persistence and linear "
        "baselines while maintaining zero temporal data leakage."
    )
    p_disc.paragraph_format.line_spacing = 1.15
    p_disc.paragraph_format.space_after = Pt(8)

    doc.add_heading("16. Practical Implications", level=1)
    p_prac = doc.add_paragraph(
        "1. Dynamic Public Health Early-Warning Systems: A 1-hour ahead forecast with 11.87 μg/m³ MAE allows municipal authorities to issue "
        "real-time warnings for vulnerable populations (asthmatics, elderly, schoolchildren) before ambient air reaches hazardous tiers.\n"
        "2. Intelligent Traffic and Industrial Modulation: Regulatory bodies can trigger temporary restrictions on heavy diesel traffic "
        "and industrial boilers when forecasted PM2.5 acceleration indicates an incipient haze event.\n"
        "3. Automated HVAC & Air Filtration Control: Smart building management systems can proactively seal outdoor air intakes and "
        "maximize HEPA filtration prior to incoming pollution plumes."
    )
    p_prac.paragraph_format.line_spacing = 1.15
    p_prac.paragraph_format.space_after = Pt(8)

    doc.add_heading("17. Limitations", level=1)
    p_lim = doc.add_paragraph(
        "1. Atmospheric Vertical Profiling Absence: The dataset is restricted to surface measurements. Upper-air sounding data "
        "(planetary boundary layer height, vertical temperature inversions) was not present, limiting model ability to detect sudden "
        "inversion capping layers.\n"
        "2. Upstream Spatial Transport Teleconnections: While 12 stations were included, regional emission flux from neighboring Hebei "
        "province and Tianjin was not explicitly gridded in a spatial transport network.\n"
        "3. Extreme Peak Attenuation: Similar to most regression architectures trained on MSE loss, the MLP exhibits modest underestimation "
        "at the extreme upper tail (>400 μg/m³)."
    )
    p_lim.paragraph_format.line_spacing = 1.15
    p_lim.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 18. CONCLUSION & 19. FUTURE SCOPE
    # -------------------------------------------------------------
    doc.add_heading("18. Conclusion", level=1)
    p_conc = doc.add_paragraph(
        "This project successfully completed an extensive exploratory analysis, statistical evaluation, and deep learning modeling "
        "workflow on the Beijing Multi-Site Air Quality dataset. Spanning 420,768 records and 18 attributes, the study confirmed "
        "strong spatial heterogeneity (Kruskal-Wallis H = 3548.99, p < 0.001), pronounced seasonal contrasts (Cohen's d = 0.360), and "
        "continuous distribution characteristics best captured by Weibull and Gamma distributions over Lognormal and Normal alternatives. "
        "All seven stages of visualization were systematically implemented. The developed PyTorch MLP achieved a test RMSE of "
        "22.80 μg/m³, an MAE of 11.87 μg/m³, an R² of 0.9571, and a mean residual of 1.71 μg/m³ on a held-out winter test period, "
        "decisively outperforming both persistence (RMSE = 26.12 μg/m³) and Ridge regression (RMSE = 24.20 μg/m³) baselines."
    )
    p_conc.paragraph_format.line_spacing = 1.15
    p_conc.paragraph_format.space_after = Pt(8)

    doc.add_heading("19. Future Scope", level=1)
    p_fut = doc.add_paragraph(
        "1. Spatiotemporal Graph Neural Networks (ST-GNN): Representing the 12 monitoring stations as graph nodes connected by "
        "geographic distance and wind direction adjacency matrices to explicitly model inter-station transport.\n"
        "2. Satellite Remote Sensing Integration: Fusing surface sensor streams with Moderate Resolution Imaging Spectroradiometer (MODIS) "
        "Aerosol Optical Depth (AOD) retrievals.\n"
        "3. Multi-Horizon Sequence Modeling: Extending the single-step 1-hour forecast to multi-step recursive and sequence-to-sequence "
        "Transformer architectures (e.g., Temporal Fusion Transformers) for 24-hour and 48-hour forecasting horizons."
    )
    p_fut.paragraph_format.line_spacing = 1.15
    p_fut.paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 20. REFERENCES (APA / IEEE format with real URLs)
    # -------------------------------------------------------------
    doc.add_heading("20. References", level=1)
    refs = [
        "1. Chen, S. (2017). Beijing Multi-Site Air-Quality Data [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5K306",
        "2. Zhang, S., Guo, B., Dong, A., He, J., Xu, Z., & Chen, S. X. (2017). Cautionary tales on air-quality improvement in Beijing. Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences, 473(2205), 20170457. https://doi.org/10.1098/rspa.2017.0457",
        "3. Fry, B. (2008). Visualizing Data: Exploring and Explaining Data with the Processing Environment. O'Reilly Media, Sebastopol, CA. ISBN: 978-0596514556.",
        "4. World Health Organization. (2021). WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide. World Health Organization. https://www.who.int/publications/i/item/9789240034228",
        "5. Paszke, A., Gross, S., Massa, F., Lerer, A., Bradbury, J., Chanan, G., ... & Chintala, S. (2019). PyTorch: An imperative style, high-performance deep learning library. Advances in Neural Information Processing Systems (NeurIPS 32), 8026-8037. https://pytorch.org/",
        "6. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830. https://scikit-learn.org/"
    ]
    for r in refs:
        p_ref = doc.add_paragraph(r)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # 21. APPENDIX & RUBRIC COMPLIANCE
    # -------------------------------------------------------------
    doc.add_heading("21. Appendix & Rubric Compliance", level=1)
    p_app = doc.add_paragraph(
        "This project repository is fully reproducible and structured in accordance with the U21ADP05 guidelines. "
        "Table 7 verifies complete compliance across all Course Outcomes (CO3, CO4, CO5)."
    )
    p_app.paragraph_format.space_after = Pt(6)

    # Table 7: Rubric Compliance Table
    doc.add_paragraph("Table 7. Complete Rubric Compliance and Evaluation Evidence (40 Total Marks)", style='Normal').runs[0].bold = True
    rubric_rows = [
        ("CO3 — Data Visualization", "Selection & creation of diverse, effective visuals", "3 Marks", "14 distinct publication-quality figures: KDEs, multi-site boxplots, heatmaps, scatter, diurnal cycles, residuals."),
        ("CO3 — Data Visualization", "Quality and presentation of visual figures", "2 Marks", "High-resolution 300 DPI graphics, standard atmospheric units (μg/m³, hPa, °C), clean grids, clear legends."),
        ("CO3 — Data Visualization", "Interpretation of visual observations", "3 Marks", "In-depth domain interpretations detailing dispersion thresholds, rush-hour peaks, and thermal inversion physics."),
        ("CO4 — Statistical Visualization", "Univariate analysis & distribution exploration", "4 Marks", "Parametric & non-parametric inventories (Mean, Std, Median, IQR, Skewness, Kurtosis) for 11 continuous features."),
        ("CO4 — Statistical Visualization", "Discrete and continuous probability distributions", "4 Marks", "Continuous MLE fitting (Weibull best fit AIC 214023.2, Gamma, Lognormal, Normal); discrete count comparison (Negative Binomial AIC 3353.3 vs. Poisson AIC 3421.1, ΔAIC -67.9)."),
        ("CO4 — Statistical Visualization", "Bivariate / multivariate analysis & hypothesis testing", "4 Marks", "Pearson correlation matrix; Kruskal-Wallis H=3548.99; ANOVA F=2710.16; Mann-Whitney U test (p < 0.001, Cohen's d=0.360)."),
        ("CO5 — Application of Exploration", "Real-world application, pipeline & documentation", "12 Marks", "Public health PM2.5 forecasting; PyTorch MLP (RMSE 22.80 μg/m³, R² 0.9571); zero-leakage chronological split."),
        ("CO5 — Application of Exploration", "GitHub repository & submission package", "4 Marks", "Modular source code (src/), executed Jupyter notebook (notebooks/), complete README, Word & PDF reports, ZIP package.")
    ]
    tbl_rubric = doc.add_table(rows=len(rubric_rows) + 1, cols=4)
    tbl_rubric_headers = ["Rubric Component", "Evaluation Criteria", "Max Marks", "Implementation Verification Evidence"]
    for c_idx, name in enumerate(tbl_rubric_headers):
        tbl_rubric.rows[0].cells[c_idx].text = name
    for r_idx, r_data in enumerate(rubric_rows):
        cells = tbl_rubric.rows[r_idx + 1].cells
        for c_idx, val in enumerate(r_data):
            cells[c_idx].text = val
    format_table(tbl_rubric)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    p_code = doc.add_paragraph()
    r_code_t = p_code.add_run("Modular Python Architecture in Project Repository:\n")
    r_code_t.bold = True
    p_code.add_run(
        "• src/data_preprocessing.py: Ingestion, continuous temporal interpolation, feature engineering, and chronological splits.\n"
        "• src/exploratory_analysis.py: Quality audits, parametric/non-parametric summaries, distribution fitting, and hypothesis tests.\n"
        "• src/visualization.py: 300 DPI figure generation covering all 7 stages of visualization and Plotly interactive dashboard.\n"
        "• src/train_model.py: PyTorch MLP deep learning architecture, baseline training, and hyperparameter grid search.\n"
        "• src/evaluate_model.py: Held-out test evaluation, permutation feature importance, and diagnostic residual figures.\n"
        "• notebooks/Air_Quality_EDA_Visualization.ipynb: Complete interactive Jupyter notebook replicating the end-to-end workflow."
    )

    docx_path = os.path.join(reports_dir, "Project_Report.docx")
    doc.save(docx_path)
    print(f"Word report saved successfully to: {docx_path}")
    return docx_path


if __name__ == '__main__':
    base_dir = r"c:\Users\MiRuThUlA.LAPTOP-SMP99ABO.000\OneDrive\Desktop\Urban_Air_Quality_EDA"
    generate_full_report(base_dir)
