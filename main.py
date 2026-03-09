"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        SUPPLIER DEPENDENCY RISK SCORER — GLOBAL PHARMA SUPPLY CHAIN         ║
║                  Developed by: Pavithra V | Data Analyst                    ║
║                  Domain: Pharmaceutical Supply Chain Analytics                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Project Overview:
-----------------
This tool scores how dangerously over-reliant a pharma supply chain is on
single-country or single-supplier sources for Active Pharmaceutical Ingredients
(APIs) and raw materials. It uses a multi-factor risk scoring model, stores all
data in a SQL database, and exports dashboards for Power BI.

Stack: Python | SQLite (SQL) | Power BI (via Excel export)

Author : Pavithra V
Email  : pavisumi1408@gmail.com
GitHub : github.com/pavi14-06
"""

import os
import sqlite3
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

warnings.filterwarnings("ignore")
init(autoreset=True)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DB_PATH     = "supplier_risk.db"
EXPORT_DIR  = "powerbi_exports"
CHARTS_DIR  = "charts"

os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────
def print_banner():
    banner = f"""
{Fore.CYAN}{'═'*72}
   🧬 SUPPLIER DEPENDENCY RISK SCORER — PHARMA SUPPLY CHAIN
   Pharma Supply Chain Analytics | Pavithra V
{'═'*72}{Style.RESET_ALL}
"""
    print(banner)


# ─────────────────────────────────────────────
# STEP 1: GENERATE SYNTHETIC PHARMA DATA
# ─────────────────────────────────────────────
def generate_pharma_data():
    """
    Simulates a realistic pharma supply chain dataset.
    In production, this would be replaced by live ERP/SQL queries.
    """
    print(Fore.YELLOW + "\n[1/6] Generating pharma supply chain dataset..." + Style.RESET_ALL)

    np.random.seed(42)

    suppliers = [
        {"supplier_id": "SUP001", "supplier_name": "SunPharma API Ltd",      "country": "India",  "region": "Asia"},
        {"supplier_id": "SUP002", "supplier_name": "WuXi BioSource",          "country": "China",  "region": "Asia"},
        {"supplier_id": "SUP003", "supplier_name": "BASF Pharma Chemicals",   "country": "Germany","region": "Europe"},
        {"supplier_id": "SUP004", "supplier_name": "Teva Raw Materials",       "country": "Israel", "region": "Middle East"},
        {"supplier_id": "SUP005", "supplier_name": "Pfizer Global Supply",    "country": "USA",    "region": "Americas"},
        {"supplier_id": "SUP006", "supplier_name": "Divi's Laboratories",     "country": "India",  "region": "Asia"},
        {"supplier_id": "SUP007", "supplier_name": "Lonza AG",                "country": "Switzerland","region": "Europe"},
        {"supplier_id": "SUP008", "supplier_name": "Zhejiang Huahai Pharma",  "country": "China",  "region": "Asia"},
        {"supplier_id": "SUP009", "supplier_name": "Dr Reddy's Chemicals",    "country": "India",  "region": "Asia"},
        {"supplier_id": "SUP010", "supplier_name": "Sanofi API Division",     "country": "France", "region": "Europe"},
    ]

    materials = [
        "Paracetamol API", "Amoxicillin API", "Metformin API",
        "Atorvastatin API", "Amlodipine API", "Ibuprofen API",
        "Azithromycin API", "Omeprazole API", "Ciprofloxacin API", "Insulin API"
    ]

    records = []
    for s in suppliers:
        for mat in np.random.choice(materials, size=np.random.randint(3, 7), replace=False):
            records.append({
                "supplier_id"            : s["supplier_id"],
                "supplier_name"          : s["supplier_name"],
                "country"                : s["country"],
                "region"                 : s["region"],
                "material"               : mat,
                "annual_spend_usd"       : round(np.random.uniform(500_000, 8_000_000), 2),
                "lead_time_days"         : np.random.randint(14, 120),
                "on_time_delivery_pct"   : round(np.random.uniform(60, 99), 1),
                "quality_reject_pct"     : round(np.random.uniform(0.1, 8.0), 2),
                "sole_source"            : np.random.choice([True, False], p=[0.35, 0.65]),
                "geopolitical_risk_score": np.random.randint(1, 10),  # 1=safe 10=high risk
                "regulatory_compliance"  : np.random.choice(["FDA", "EMA", "Both", "None"],
                                                              p=[0.3, 0.2, 0.35, 0.15]),
                "last_audit_days_ago"    : np.random.randint(30, 730),
                "disruption_incidents"   : np.random.randint(0, 6),
                "record_date"            : datetime.today().strftime("%Y-%m-%d")
            })

    df = pd.DataFrame(records)
    print(Fore.GREEN + f"   ✔ Dataset created: {len(df)} supplier-material records" + Style.RESET_ALL)
    return df, pd.DataFrame(suppliers)


# ─────────────────────────────────────────────
# STEP 2: STORE IN SQL DATABASE
# ─────────────────────────────────────────────
def store_to_sql(df_records, df_suppliers):
    print(Fore.YELLOW + "\n[2/6] Storing data into SQLite database..." + Style.RESET_ALL)

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Create tables
    cur.executescript("""
        DROP TABLE IF EXISTS supplier_master;
        DROP TABLE IF EXISTS supply_chain_records;
        DROP TABLE IF EXISTS risk_scores;

        CREATE TABLE supplier_master (
            supplier_id   TEXT PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            country       TEXT NOT NULL,
            region        TEXT NOT NULL
        );

        CREATE TABLE supply_chain_records (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id             TEXT,
            material                TEXT,
            annual_spend_usd        REAL,
            lead_time_days          INTEGER,
            on_time_delivery_pct    REAL,
            quality_reject_pct      REAL,
            sole_source             INTEGER,
            geopolitical_risk_score INTEGER,
            regulatory_compliance   TEXT,
            last_audit_days_ago     INTEGER,
            disruption_incidents    INTEGER,
            record_date             TEXT,
            FOREIGN KEY (supplier_id) REFERENCES supplier_master(supplier_id)
        );

        CREATE TABLE risk_scores (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id     TEXT,
            supplier_name   TEXT,
            country         TEXT,
            region          TEXT,
            composite_score REAL,
            risk_tier       TEXT,
            scored_on       TEXT
        );
    """)

    df_suppliers.to_sql("supplier_master",     conn, if_exists="replace", index=False)
    df_records.to_sql  ("supply_chain_records", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print(Fore.GREEN + f"   ✔ Data saved to '{DB_PATH}'" + Style.RESET_ALL)


# ─────────────────────────────────────────────
# STEP 3: RISK SCORING ENGINE (SQL + Python)
# ─────────────────────────────────────────────
def compute_risk_scores():
    """
    Multi-factor risk scoring model:
    - Sole source dependency       (30%)
    - Geopolitical risk            (20%)
    - Lead time risk               (15%)
    - Delivery performance         (15%)
    - Quality rejection rate       (10%)
    - Audit recency                (5%)
    - Disruption history           (5%)
    """
    print(Fore.YELLOW + "\n[3/6] Computing supplier dependency risk scores..." + Style.RESET_ALL)

    conn = sqlite3.connect(DB_PATH)

    # SQL aggregation query
    query = """
        SELECT
            s.supplier_id,
            s.supplier_name,
            s.country,
            s.region,
            AVG(r.sole_source)             AS avg_sole_source,
            AVG(r.geopolitical_risk_score) AS avg_geo_risk,
            AVG(r.lead_time_days)          AS avg_lead_time,
            AVG(r.on_time_delivery_pct)    AS avg_on_time,
            AVG(r.quality_reject_pct)      AS avg_quality_reject,
            AVG(r.last_audit_days_ago)     AS avg_audit_days,
            SUM(r.disruption_incidents)    AS total_disruptions,
            COUNT(*)                       AS total_materials,
            SUM(r.annual_spend_usd)        AS total_spend
        FROM supplier_master s
        JOIN supply_chain_records r ON s.supplier_id = r.supplier_id
        GROUP BY s.supplier_id, s.supplier_name, s.country, s.region
    """
    df_agg = pd.read_sql_query(query, conn)

    # Normalize each factor to 0–100
    def normalize(series, invert=False):
        mn, mx = series.min(), series.max()
        if mx == mn:
            return pd.Series([50.0] * len(series), index=series.index)
        norm = (series - mn) / (mx - mn) * 100
        return 100 - norm if invert else norm

    df_agg["score_sole_source"]  = normalize(df_agg["avg_sole_source"])      * 30 / 100
    df_agg["score_geo"]          = normalize(df_agg["avg_geo_risk"])          * 20 / 100
    df_agg["score_lead_time"]    = normalize(df_agg["avg_lead_time"])         * 15 / 100
    df_agg["score_delivery"]     = normalize(df_agg["avg_on_time"], True)     * 15 / 100
    df_agg["score_quality"]      = normalize(df_agg["avg_quality_reject"])    * 10 / 100
    df_agg["score_audit"]        = normalize(df_agg["avg_audit_days"])        *  5 / 100
    df_agg["score_disruptions"]  = normalize(df_agg["total_disruptions"])     *  5 / 100

    df_agg["composite_score"] = (
        df_agg["score_sole_source"] + df_agg["score_geo"]      +
        df_agg["score_lead_time"]   + df_agg["score_delivery"]  +
        df_agg["score_quality"]     + df_agg["score_audit"]     +
        df_agg["score_disruptions"]
    ).round(2)

    # Risk tiers
    def assign_tier(score):
        if score >= 60: return "🔴 CRITICAL"
        elif score >= 40: return "🟠 HIGH"
        elif score >= 25: return "🟡 MEDIUM"
        else: return "🟢 LOW"

    df_agg["risk_tier"] = df_agg["composite_score"].apply(assign_tier)
    df_agg["scored_on"] = datetime.today().strftime("%Y-%m-%d")

    # Save risk scores to SQL
    df_scores = df_agg[["supplier_id","supplier_name","country","region",
                         "composite_score","risk_tier","scored_on"]]
    df_scores.to_sql("risk_scores", conn, if_exists="replace", index=False)
    conn.close()

    print(Fore.GREEN + "   ✔ Risk scores computed and saved to SQL" + Style.RESET_ALL)
    return df_agg


# ─────────────────────────────────────────────
# STEP 4: DISPLAY RESULTS
# ─────────────────────────────────────────────
def display_results(df_agg):
    print(Fore.YELLOW + "\n[4/6] Supplier Risk Scorecard:" + Style.RESET_ALL)

    display_df = df_agg[[
        "supplier_name", "country", "composite_score", "risk_tier",
        "total_materials", "total_spend"
    ]].sort_values("composite_score", ascending=False).reset_index(drop=True)

    display_df["total_spend"] = display_df["total_spend"].apply(lambda x: f"${x:,.0f}")
    display_df.columns = ["Supplier", "Country", "Risk Score", "Risk Tier", "# Materials", "Total Spend"]

    print(tabulate(display_df, headers="keys", tablefmt="fancy_grid", showindex=True))

    # Country-level dependency
    print(Fore.CYAN + "\n   📊 Country Dependency Summary:" + Style.RESET_ALL)
    country_risk = df_agg.groupby("country")["composite_score"].mean().sort_values(ascending=False)
    for country, score in country_risk.items():
        bar = "█" * int(score / 5)
        color = Fore.RED if score >= 60 else Fore.YELLOW if score >= 40 else Fore.GREEN
        print(f"   {color}{country:<15} {bar:<20} {score:.1f}{Style.RESET_ALL}")


# ─────────────────────────────────────────────
# STEP 5: GENERATE CHARTS
# ─────────────────────────────────────────────
def generate_charts(df_agg):
    print(Fore.YELLOW + "\n[5/6] Generating analytical charts..." + Style.RESET_ALL)

    palette = {"🔴 CRITICAL": "#E74C3C", "🟠 HIGH": "#E67E22",
               "🟡 MEDIUM": "#F1C40F", "🟢 LOW": "#27AE60"}

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Supplier Dependency Risk Scorer — Pharma Supply Chain\nDeveloped by Pavithra V",
                 fontsize=14, fontweight="bold", color="#2C3E50")
    fig.patch.set_facecolor("#F8F9FA")

    # Chart 1: Risk Score Bar
    ax1 = axes[0, 0]
    df_sorted = df_agg.sort_values("composite_score", ascending=True)
    colors = [palette.get(t, "#95A5A6") for t in df_sorted["risk_tier"]]
    bars = ax1.barh(df_sorted["supplier_name"], df_sorted["composite_score"], color=colors, edgecolor="white")
    ax1.set_xlabel("Composite Risk Score (0–100)", fontsize=10)
    ax1.set_title("Supplier Risk Scores", fontweight="bold")
    ax1.axvline(x=60, color="#E74C3C", linestyle="--", alpha=0.5, label="Critical Threshold")
    ax1.axvline(x=40, color="#E67E22", linestyle="--", alpha=0.5, label="High Threshold")
    ax1.legend(fontsize=8)
    ax1.set_facecolor("#FAFAFA")

    # Chart 2: Country Risk Heatmap
    ax2 = axes[0, 1]
    country_data = df_agg.groupby("country")["composite_score"].mean().reset_index()
    country_data.columns = ["Country", "Avg Risk Score"]
    country_data = country_data.sort_values("Avg Risk Score", ascending=False)
    bar_colors = ["#E74C3C" if s >= 60 else "#E67E22" if s >= 40 else "#F1C40F" if s >= 25 else "#27AE60"
                  for s in country_data["Avg Risk Score"]]
    ax2.bar(country_data["Country"], country_data["Avg Risk Score"], color=bar_colors, edgecolor="white")
    ax2.set_title("Average Risk Score by Country", fontweight="bold")
    ax2.set_ylabel("Avg Risk Score")
    ax2.set_xticklabels(country_data["Country"], rotation=30, ha="right")
    ax2.set_facecolor("#FAFAFA")

    # Chart 3: Risk Tier Distribution (Pie)
    ax3 = axes[1, 0]
    tier_counts = df_agg["risk_tier"].value_counts()
    pie_colors  = [palette.get(t, "#95A5A6") for t in tier_counts.index]
    ax3.pie(tier_counts.values, labels=tier_counts.index, colors=pie_colors,
            autopct="%1.1f%%", startangle=140, textprops={"fontsize": 9})
    ax3.set_title("Risk Tier Distribution", fontweight="bold")

    # Chart 4: Spend vs Risk Scatter
    ax4 = axes[1, 1]
    scatter_colors = [palette.get(t, "#95A5A6") for t in df_agg["risk_tier"]]
    sc = ax4.scatter(df_agg["total_spend"] / 1e6, df_agg["composite_score"],
                     c=scatter_colors, s=120, edgecolors="white", linewidths=1.5, alpha=0.85)
    for _, row in df_agg.iterrows():
        ax4.annotate(row["supplier_id"], (row["total_spend"] / 1e6, row["composite_score"]),
                     fontsize=7, alpha=0.7)
    ax4.set_xlabel("Total Annual Spend (USD Millions)", fontsize=10)
    ax4.set_ylabel("Composite Risk Score", fontsize=10)
    ax4.set_title("Spend vs Risk: High-Spend High-Risk Quadrant", fontweight="bold")
    ax4.axhline(y=60, color="#E74C3C", linestyle="--", alpha=0.4)
    ax4.axhline(y=40, color="#E67E22", linestyle="--", alpha=0.4)
    ax4.set_facecolor("#FAFAFA")

    plt.tight_layout()
    chart_path = os.path.join(CHARTS_DIR, "risk_dashboard.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(Fore.GREEN + f"   ✔ Charts saved → {chart_path}" + Style.RESET_ALL)


# ─────────────────────────────────────────────
# STEP 6: EXPORT TO EXCEL (Power BI Input)
# ─────────────────────────────────────────────
def export_for_powerbi(df_agg, df_records):
    print(Fore.YELLOW + "\n[6/6] Exporting Power BI–ready Excel files..." + Style.RESET_ALL)

    conn = sqlite3.connect(DB_PATH)

    # Full enriched dataset
    full_df = pd.read_sql_query("""
        SELECT
            s.supplier_name, s.country, s.region, r.material,
            r.annual_spend_usd, r.lead_time_days, r.on_time_delivery_pct,
            r.quality_reject_pct, r.sole_source, r.geopolitical_risk_score,
            r.regulatory_compliance, r.last_audit_days_ago, r.disruption_incidents,
            rs.composite_score, rs.risk_tier
        FROM supply_chain_records r
        JOIN supplier_master s ON r.supplier_id = s.supplier_id
        JOIN risk_scores rs ON r.supplier_id = rs.supplier_id
    """, conn)

    risk_df = pd.read_sql_query("SELECT * FROM risk_scores ORDER BY composite_score DESC", conn)
    conn.close()

    excel_path = os.path.join(EXPORT_DIR, "supplier_risk_powerbi.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        full_df.to_excel(writer, sheet_name="Full_Supply_Chain_Data", index=False)
        risk_df.to_excel(writer, sheet_name="Risk_Scores_Summary",    index=False)

        # Country roll-up
        country_rollup = df_agg.groupby(["country", "region"]).agg(
            avg_risk_score=("composite_score", "mean"),
            supplier_count=("supplier_id", "count"),
            total_spend=("total_spend", "sum")
        ).reset_index()
        country_rollup.to_excel(writer, sheet_name="Country_Risk_Rollup", index=False)

        # Material risk
        material_risk = full_df.groupby("material").agg(
            avg_risk_score=("composite_score", "mean"),
            supplier_count=("supplier_name", "nunique"),
            total_spend=("annual_spend_usd", "sum")
        ).reset_index().sort_values("avg_risk_score", ascending=False)
        material_risk.to_excel(writer, sheet_name="Material_Risk_View", index=False)

    print(Fore.GREEN + f"   ✔ Power BI export saved → {excel_path}" + Style.RESET_ALL)
    print(Fore.CYAN  + "      Sheets: Full_Supply_Chain_Data | Risk_Scores_Summary | Country_Risk_Rollup | Material_Risk_View" + Style.RESET_ALL)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print_banner()

    df_records, df_suppliers = generate_pharma_data()
    store_to_sql(df_records, df_suppliers)
    df_agg = compute_risk_scores()
    display_results(df_agg)
    generate_charts(df_agg)
    export_for_powerbi(df_agg, df_records)

    print(Fore.CYAN + f"""
{'═'*72}
  ✅  PIPELINE COMPLETE
  📁  Database  : {DB_PATH}
  📊  Charts    : {CHARTS_DIR}/risk_dashboard.png
  📋  Power BI  : {EXPORT_DIR}/supplier_risk_powerbi.xlsx
{'═'*72}
    """ + Style.RESET_ALL)


if __name__ == "__main__":
    main()
