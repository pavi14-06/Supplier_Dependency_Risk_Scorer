# 🧬 Supplier Dependency Risk Scorer
### Pharma Supply Chain Intelligence

> **Built by Pavithra V** — Data Analyst | Python · SQL · Power BI  
> 📧 pavisumi1408@gmail.com | 🔗 [LinkedIn](https://linkedin.com/in/pavithra-v-56bb87280) | 🌐 [Portfolio](https://pavithra-v-portfolio.netlify.app)

---

## 🎯 Problem Statement

Pharmaceutical companies sourcing Active Pharmaceutical Ingredients (APIs) from a concentrated set of countries (e.g., China, India) face catastrophic supply disruption risks. The COVID-19 pandemic exposed how **over-reliance on single-country or sole-source suppliers** can halt drug production globally.

This project builds a **data-driven risk scoring engine** that quantifies supplier dependency risk across multiple dimensions — giving pharma analysts an early-warning system before disruptions happen.

---

## 💡 What It Does

- **Ingests** supplier-material supply chain data (ERP-simulated)
- **Stores** all data in a structured **SQL database** with normalized schema
- **Scores** each supplier using a **multi-factor weighted risk model**
- **Classifies** suppliers into 4 risk tiers: 🔴 Critical → 🟠 High → 🟡 Medium → 🟢 Low
- **Exports** Power BI–ready Excel with 4 analytical sheets
- **Visualizes** risk via a 4-panel analytical dashboard

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Database | SQLite (SQL) |
| Visualization | Matplotlib, Seaborn |
| BI Export | OpenPyXL → Power BI |
| ML Ready | Scikit-learn (normalization) |

---

## 📊 Risk Scoring Model

The composite score (0–100) is calculated from 7 weighted factors:

| Factor | Weight | Logic |
|--------|--------|-------|
| Sole Source Dependency | **30%** | Single supplier = maximum risk |
| Geopolitical Risk Score | **20%** | Country stability index (1–10) |
| Lead Time Risk | **15%** | Longer lead times = higher exposure |
| Delivery Performance | **15%** | Low on-time % = operational risk |
| Quality Rejection Rate | **10%** | High reject % = quality dependency |
| Audit Recency | **5%** | Overdue audits = compliance gap |
| Disruption History | **5%** | Past incidents predict future risk |

### Risk Tiers
```
Score ≥ 60  →  🔴 CRITICAL   — Immediate mitigation required
Score 40–59 →  🟠 HIGH       — Strategic review needed
Score 25–39 →  🟡 MEDIUM     — Monitor and diversify
Score < 25  →  🟢 LOW        — Acceptable dependency
```

---

## 📁 Project Structure

```
supplier-risk-scorer/
│
├── main.py                          # Core pipeline (end-to-end)
├── queries.sql                      # 6 analytical SQL query library
├── requirements.txt                 # Python dependencies
│
├── supplier_risk.db                 # SQLite DB (auto-generated)
│
├── powerbi_exports/
│   └── supplier_risk_powerbi.xlsx  # 4-sheet Power BI input file
│
├── charts/
│   └── risk_dashboard.png          # 4-panel analytical dashboard
│
└── README.md
```

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/pavi14-06/supplier-dependency-risk-scorer.git
cd supplier-dependency-risk-scorer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python main.py
```

---

## 📋 SQL Query Library (`queries.sql`)

6 production-ready queries for analyst use:

| Query | Purpose |
|-------|---------|
| `Q1` | Full supplier risk dashboard view |
| `Q2` | Country-level dependency analysis |
| `Q3` | Sole-source critical materials |
| `Q4` | High-risk supplier watchlist |
| `Q5` | Regulatory compliance gap report |
| `Q6` | Spend-risk concentration index |

---

## 📈 Power BI Dashboard Setup

After running `main.py`, open `powerbi_exports/supplier_risk_powerbi.xlsx` in Power BI Desktop:

1. **Get Data** → Excel → select `supplier_risk_powerbi.xlsx`
2. Load all 4 sheets:
   - `Full_Supply_Chain_Data` → Detail table
   - `Risk_Scores_Summary` → KPI cards + scorecard
   - `Country_Risk_Rollup` → Map visual + bar chart
   - `Material_Risk_View` → Material heatmap
3. Build relationships on `supplier_id`
4. Use DAX measure: `Avg Risk Score = AVERAGE(Risk_Scores_Summary[composite_score])`

---

## 📸 Output Preview

### Risk Dashboard (Auto-Generated)
- Supplier risk score bar chart
- Country dependency heatmap
- Risk tier distribution (pie)
- Spend vs Risk scatter (quadrant analysis)

---

## 🔬 Real-World Extensions

- Connect to live **ERP systems** (SAP, eChain ChainSys) via API
- Add **ARIMA forecasting** for lead time trend prediction
- Integrate **WHO/CDC outbreak data** as geopolitical risk signals
- Automate alerts via email when suppliers cross risk thresholds
- Deploy as a **Power BI Embedded** web app for stakeholders

---

## 👩‍💻 About the Author

**Pavithra V** — Software Engineer & Data Analyst  
Experienced in ERP analytics, supply chain dashboards, and ML-powered reporting for aerospace/defense at **Data Patterns India Ltd**.

> *"Transforming complex supply chain data into risk intelligence that protects patient access to medicines."*

---

## 📄 License

MIT License — Free to use with attribution.
