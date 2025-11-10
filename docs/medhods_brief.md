# Statistical Methods Brief
## Child Welfare Capstone Project

**Author**: Ali Karaduman  
**Date**: November 2024  
**Version**: 1.0

---

## Table of Contents
1. [Overview](#overview)
2. [Data Sources & Structure](#data-sources--structure)
3. [Exploratory Data Analysis](#exploratory-data-analysis)
4. [Multilevel Mixed-Effects Modeling](#multilevel-mixed-effects-modeling)
5. [Survival Analysis](#survival-analysis)
6. [Natural Language Processing](#natural-language-processing)
7. [Policy Simulation & Causal Inference](#policy-simulation--causal-inference)
8. [Limitations & Considerations](#limitations--considerations)

---

## Overview

This document provides technical details on the statistical methods employed in the Child Welfare Data Analytics capstone project. The analysis combines multiple advanced techniques to understand, predict, and propose interventions for extended foster care stays.

**Primary Research Question**: What factors predict extended foster care stays (3+ years), and how can policy interventions reduce long-stay rates?

---

## Data Sources & Structure

### Database Design
- **RDBMS**: PostgreSQL 16
- **Tables**: 7 core tables (normalized schema)
- **Records**: ~500 children, ~400 episodes, 2,500+ case notes
- **Time Period**: 2021-2025 (synthetic data)

### Key Variables

#### Outcome Variable
- **Long-Stay Status**: Binary indicator (1 = 3+ years in care, 0 = <3 years)
- **Episode Length**: Continuous (days in care)

#### Predictor Variables
- **Child-Level**: Age at entry, race/ethnicity, gender, removal reason
- **Episode-Level**: Total placements, placement types, service provision
- **County-Level**: Geographic location, county resources
- **Text-Level**: Case note topics (derived via NLP)

---

## Exploratory Data Analysis

### Methods
1. **Univariate Analysis**
   - Distribution checks (histograms, Q-Q plots)
   - Skewness and kurtosis assessment
   - Outlier detection (IQR method)

2. **Bivariate Analysis**
   - Pearson/Spearman correlations
   - Chi-square tests for categorical associations
   - T-tests and ANOVA for group comparisons

3. **Temporal Analysis**
   - Time series visualization
   - Seasonal decomposition
   - Trend identification

### Key Findings
- Length of stay is **right-skewed** (median = 734 days)
- Strong **correlation** between placements and long-stay (r = 0.23)
- **County-level variation**: 14.7% to 28.3% long-stay rates
- **Demographic disparities**: Some groups over-represented in long-stays

---

## Multilevel Mixed-Effects Modeling

### Rationale
Children are **nested within counties**, creating hierarchical data structure. Standard regression assumes independence, which is violated. Multilevel models account for:
- Clustering of observations within counties
- Between-county vs. within-county variation
- County-level random effects

### Model Specification

**Level 1 (Child-Level)**:logit(P(Long-Stay_ij)) = β₀j + β₁(Age_ij) + β₂(Race_ij) + β₃(Placements_ij) + ε_ij

**Level 2 (County-Level)**:β₀j = γ₀₀ + γ₀₁(County_Resources_j) + u₀j

Where:
- `i` = individual child
- `j` = county
- `β₀j` = random intercept for county j
- `u₀j` = county-level random effect
- `ε_ij` = child-level residual

### Implementation
**Software**: Python `statsmodels.MixedLM`

**Model Family**: Generalized Linear Mixed Model (GLMM) with logit link

**Estimation**: Maximum Likelihood Estimation (MLE)

### Results

#### Fixed Effects
| Predictor | Coefficient | Std. Error | p-value |
|-----------|-------------|------------|---------|
| Intercept | -1.23 | 0.18 | <0.001 |
| Age at Entry | 0.05 | 0.02 | 0.012 |
| Race (Black) | 0.31 | 0.12 | 0.009 |
| Total Placements | 0.15 | 0.03 | <0.001 |

#### Random Effects
- **County Variance (τ²)**: 0.42
- **Residual Variance (σ²)**: 1.68
- **ICC**: 0.20 (20% of variance is between counties)

#### Model Fit
- **AIC**: 432.5
- **BIC**: 456.8
- **Pseudo R²**: 0.25
- **Log-Likelihood**: -210.3

### Interpretation
- **ICC = 0.20**: 20% of variation in long-stay outcomes is attributable to county-level differences
- **Placement coefficient (0.15)**: Each additional placement increases log-odds of long-stay by 0.15
- County-level interventions could theoretically reduce up to 20% of outcome variation

---

## Survival Analysis

### Cox Proportional Hazards Model

**Purpose**: Model time-to-exit from foster care, accounting for censored observations (children still in care)

**Model**:h(t|X) = h₀(t) × exp(β₁X₁ + β₂X₂ + ... + βₚXₚ)

Where:
- `h(t|X)` = hazard at time t given covariates X
- `h₀(t)` = baseline hazard
- Hazard ratio for covariate X: `HR = exp(β)`

### Assumptions
1. **Proportional Hazards**: HR is constant over time
2. **Non-informative Censoring**: Censoring is independent of event
3. **Linearity**: Linear relationship between log-hazard and covariates

**Validation**:
- Schoenfeld residuals test (p > 0.05 for all covariates)
- Log-log survival plots (parallel lines confirmed)

### Key Results
| Covariate | Hazard Ratio | 95% CI | p-value | Interpretation |
|-----------|--------------|--------|---------|----------------|
| Age 0-5 | 1.23 | [1.08, 1.41] | 0.002 | 23% faster exit |
| 3+ Placements | 0.67 | [0.54, 0.83] | <0.001 | 33% slower exit |
| Neglect (vs Abuse) | 1.15 | [0.98, 1.35] | 0.089 | No sig. difference |

**Interpretation**: Children with 3+ placements have 33% lower hazard of exiting care (i.e., stay longer)

---

## Natural Language Processing

### Objective
Extract thematic patterns from 2,500+ unstructured case notes to identify linguistic indicators of outcomes.

### Preprocessing Pipeline
1. **Text Cleaning**
   - Lowercase conversion
   - Punctuation removal
   - Stop word removal (NLTK English corpus)
   - Lemmatization (spaCy)

2. **Tokenization**
   - Word-level tokens
   - Bigram/trigram extraction (Gensim Phrases)

3. **Vectorization**
   - TF-IDF (Term Frequency-Inverse Document Frequency)
   - Parameters: max_features=1000, min_df=5, max_df=0.8

### Topic Modeling (LDA)

**Algorithm**: Latent Dirichlet Allocation

**Implementation**: Gensim LdaMulticore

**Parameters**:
- Number of topics: 5 (determined via coherence score optimization)
- Passes: 20
- Alpha: 'auto' (symmetric Dirichlet prior)
- Eta: 'auto' (symmetric Dirichlet prior)

**Coherence Score**: 0.52 (C_v metric)

### Identified Topics

| Topic ID | Label | Top Keywords | Prevalence |
|----------|-------|--------------|------------|
| 0 | Assessment & Services | therapy, evaluation, referral, mental, health | 23% |
| 1 | Court & Legal | hearing, judge, attorney, petition, order | 19% |
| 2 | Visitation & Contact | visit, parent, family, contact, supervised | 21% |
| 3 | Placement & Stability | foster, home, move, placement, stable | 18% |
| 4 | Safety & Wellbeing | school, behavior, safety, medical, progress | 19% |

### Association with Outcomes
- **Correlation Analysis**: Topic distributions vs. long-stay status
- **Significant Topics**:
  - Topic 0 (Services): r = 0.23, p < 0.01 (more in long-stays)
  - Topic 2 (Visitation): r = -0.18, p < 0.05 (less in long-stays)

**Interpretation**: Language about intensive services predicts longer stays; family reunification language predicts shorter stays.

---

## Policy Simulation & Causal Inference

### Methodology

**Framework**: Potential Outcomes Framework (Rubin Causal Model)

**Simulation Type**: Monte Carlo (1,000 iterations per scenario)

### Scenarios Tested

1. **Reduce Placements**: 20% reduction in placement moves
2. **Reduce Length**: 15% reduction in episode duration
3. **County Improvements**: 50% improvement toward best-performing county
4. **Combined**: All interventions simultaneously

### Simulation Algorithm
```pythonfor simulation in range(1000):
# 1. Sample from baseline data
sample = bootstrap_sample(df)# 2. Apply intervention
sample['placements_new'] = sample['placements'] * (1 - reduction_pct)# 3. Predict outcomes
sample['prob_longstay'] = model.predict(sample)# 4. Calculate metrics
new_longstay_rate = (sample['prob_longstay'] > 0.5).mean()
prevented_cases = baseline_rate - new_longstay_rate# 5. Store results
results.append({'rate': new_longstay_rate, 'prevented': prevented_cases})

### Cost-Benefit Analysis

**Cost Parameters** (per child per day):
- Foster care: $50
- Case management: $25
- Services: $15
- Overhead: $10
- **Total**: $100/day

**Intervention Costs** (one-time per child):
- Placement stability program: $5,000
- Early service provision: $3,500
- County training: $2,000

**Financial Metrics**:ROI = (Gross Savings - Intervention Cost) / Intervention Cost × 100%
Benefit-Cost Ratio = Gross Savings / Intervention Cost

### Results Summary

| Scenario | Long-Stay Rate | Cases Prevented | ROI | BCR |
|----------|----------------|-----------------|-----|-----|
| Baseline | 21.0% | 0 | - | - |
| Reduce Placements | 21.0% | 84 | **51.5%** | **1.52** |
| Reduce Length | 9.9% | 44 | -20.1% | 0.80 |
| County Improvements | 19.3% | 7 | -88.1% | 0.12 |
| Combined | 9.9% | 44 | -20.1% | 0.80 |

### Statistical Significance

**Method**: Bootstrap confidence intervals (95%) + t-tests

**Example** (Reduce Placements scenario):
- Mean prevented: 84 cases
- 95% CI: [76, 92]
- t-statistic vs. baseline: 12.4
- p-value: <0.001

---

## Limitations & Considerations

### Data Limitations
1. **Synthetic Data**: Analysis based on simulated data modeled after AFCARS standards
2. **Sample Size**: ~400 episodes may limit power for subgroup analyses
3. **Missing Data**: Some variables have <5% missingness (handled via listwise deletion)
4. **Time Period**: Limited to 4-year window (2021-2025)

### Methodological Limitations
1. **Causal Inference**: Simulations assume no unmeasured confounding
2. **Model Assumptions**: Linearity, proportional hazards, etc. may not hold perfectly
3. **Generalizability**: Results specific to this sample and time period
4. **Cost Estimates**: Hypothetical costs; actual implementation may vary

### Ethical Considerations
1. **Privacy**: All data synthetic; no real PII used
2. **Equity**: Careful attention to racial disparities and bias
3. **Interpretability**: Models designed for transparency
4. **Stakeholder Input**: Recommendations should involve child welfare professionals

---

## References

1. Raudenbush, S. W., & Bryk, A. S. (2002). *Hierarchical linear models*. Sage.
2. Cox, D. R. (1972). Regression models and life-tables. *Journal of the Royal Statistical Society*, Series B, 34(2), 187-220.
3. Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet allocation. *Journal of Machine Learning Research*, 3, 993-1022.
4. Gelman, A., & Hill, J. (2006). *Data analysis using regression and multilevel/hierarchical models*. Cambridge University Press.
5. U.S. DHHS. (2023). *AFCARS Data Standards*. Administration for Children and Families.

---

## Appendix: Software & Packages

**Python Version**: 3.12.1

**Key Packages**:
- `pandas` 2.0.3 (data manipulation)
- `numpy` 1.24.3 (numerical computing)
- `statsmodels` 0.14.0 (statistical modeling)
- `scikit-learn` 1.3.0 (machine learning)
- `scipy` 1.11.1 (scientific computing)
- `matplotlib` 3.7.2 (visualization)
- `seaborn` 0.12.2 (statistical visualization)
- `gensim` 4.3.1 (topic modeling)
- `spacy` 3.6.0 (NLP)
- `psycopg2` 2.9.6 (PostgreSQL adapter)

**Database**: PostgreSQL 16.0

---

**Last Updated**: November 10, 2024
