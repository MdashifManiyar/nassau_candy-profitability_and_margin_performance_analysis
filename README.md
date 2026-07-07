# 🍬 Nassau Candy — Sales & Profitability Analytics Dashboard

> An end-to-end exploratory data analysis project that identifies profit drivers, cost risks, and product-level margin inefficiencies for a confectionery distributor using Python and Streamlit.

---

## 📌 Overview

Nassau Candy Distributor operates across three product divisions — Chocolate, Sugar, and Other — selling confectionery products through four regional markets. Despite tracking overall revenue, the organization had no structured view of which products, divisions, or cost structures were actually driving or eroding profitability.

This project performs a complete data analytics workflow — from raw data validation to an interactive 5-tab Streamlit dashboard — covering 10,194 order-level transactions recorded between January 2024 and December 2025. Every finding is grounded in directly computed, auditable metrics and translated into concrete business recommendations.

---

## ❗ Problem Statement

The organization lacked visibility into four core business questions:

- Which product lines deliver the highest gross margin?
- Whether high-sales products are actually profitable?
- How profitability varies across product divisions?
- Which products represent margin risk?

Without clear answers, decisions around pricing, supplier negotiation, and product discontinuation remained intuition-driven rather than data-driven.

---

## 🗂 Dataset

| Attribute | Details |
|---|---|
| **Source** | Nassau Candy Distributor — internal transactional sales data |
| **Records** | 10,194 order-level rows |
| **Time Period** | January 2024 – December 2025 |
| **Products** | 15 unique confectionery SKUs |
| **Divisions** | Chocolate, Sugar, Other |
| **Regions** | Interior, Atlantic, Gulf, Pacific |
| **Key Fields** | Order Date, Division, Region, Product Name, Units, Sales, Cost, Gross Profit |
| **Data Quality** | Zero nulls · Zero duplicates · Zero invalid records after validation |

---

## 🛠 Tools and Technologies

| Tool | Purpose |
|---|---|
| **Python 3.11** | Core programming language |
| **Pandas** | Data cleaning, validation, and KPI computation |
| **Plotly** | Interactive charts and visualizations |
| **Streamlit** | Web application and dashboard framework |
| **VS Code** | Development environment |

---

## 🔬 Methods

**1. Data Cleaning & Validation**
Programmatically validated the dataset for negative/zero sales, invalid profit records, missing units, and inconsistent labels. No rows required removal — all 10,194 records passed validation.

**2. KPI Calculation**
Computed five core metrics at the product level:
- `Gross Margin % = Gross Profit ÷ Sales × 100`
- `Profit per Unit = Gross Profit ÷ Units`
- `Revenue Contribution % = Product Sales ÷ Total Sales × 100`
- `Profit Contribution % = Product Profit ÷ Total Profit × 100`
- `Cost Ratio = Cost ÷ Sales`
- `Margin Volatility = Population std. deviation of per-order margin`

**3. Product Profitability Analysis**
Ranked all 15 products by both Gross Margin % and Gross Profit. Classified products into three groups — High-Profit/High-Margin, High-Sales/Low-Margin, and Low-Sales/Low-Profit — using median-based thresholds.

**4. Division Performance Analysis**
Aggregated revenue, profit, and margin by division. Compared cost ratios to classify divisions as either financially efficient or structurally problematic.

**5. Pareto (80/20) Analysis**
Computed cumulative profit and revenue contribution to identify which products cross the 80% threshold. Flagged over-dependency risk.

**6. Cost Structure Diagnostics**
Plotted Cost Ratio vs Gross Margin % to classify products into a 2×2 risk matrix — Star, Reprice, Volume Play, and Discontinue — using thresholds of cost ratio ≥ 0.40 and margin ≤ 60%.

---

## 💡 Key Insights

- **Overall gross margin is 65.91%** — but this average masks critical variation at the product and division level
- **Chocolate division** drives 92.88% of revenue and 95.06% of profit at a 67.45% margin
- **Other division** trails at 44.84% margin with a 0.55 cost ratio — a structural cost issue, not a pricing issue
- **3 products** (Kazookles, Lickable Wallpaper, Wonka Gum) are high-sales but low-margin, appearing profitable on revenue reports while quietly eroding margin
- **5 of 15 products** (33% of the catalog) generate over 95% of total gross profit — extreme concentration risk
- **7 products** are flagged for cost renegotiation, repricing, or discontinuation review
- **Kazookles** is the most severe case — cost ratio of 0.92, meaning 92 cents of every sales dollar is consumed by cost
- **Margin volatility = 0** across all 15 products — confirming fixed per-unit pricing, meaning margin improvement requires a deliberate price or cost change

---

## 📊 Dashboard / Output

The Streamlit dashboard is organized into **5 interactive tabs**:

| Tab | Content |
|---|---|
| 📦 **Product Profitability** | Margin leaderboard, profit ranking, contribution comparison, 3-way product classification |
| 🏭 **Division Performance** | Revenue vs profit grouped bar, avg margin by division, efficiency classification |
| 💰 **Cost Diagnostics** | Cost vs sales scatter, 2×2 risk matrix, flagged products table |
| 📊 **Pareto Analysis** | Profit & revenue Pareto charts, 80% threshold line, over-dependency risk indicator |
| 🎯 **Problem, Solution & Insights** | Direct data-backed answers to all 4 business questions + Executive Summary |

**Sidebar Filters:** Division (multi-select) · Region · Minimum Margin % (slider) · Date Range · Product Search · Reset All Filters

---

## ▶️ How to Run this Project?

**Step 1 — Clone the repository**
```bash
git clone https://github.com/<your-username>/nassau-candy-dashboard.git
cd nassau-candy-dashboard
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — (Optional) Run data cleaning**
```bash
python data_cleaning.py
```

**Step 4 — Launch the dashboard**
```bash
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## 📈 Results & Conclusion

This analysis successfully answered all four business questions with direct, data-backed results:

1. **Gross margin leadership** — Everlasting Gobstopper (80%) and Hair Toffee (77.78%) lead on margin, but Wonka Bar – Nutty Crunch Surprise (71.35%) is the strongest performer at meaningful sales volume
2. **High sales ≠ profitability** — Three products sell well but fall below median margin, proving that revenue-based reporting alone is misleading
3. **Division profitability varies sharply** — Chocolate and Sugar show strong financial efficiency; Other division has a structural cost problem requiring supplier-side intervention
4. **7 margin-risk products identified** — Kazookles is the most urgent, with 92% of revenue consumed by cost; five others require repricing or renegotiation

The project demonstrates that moving from intuition-driven to data-driven decision-making allows Nassau Candy to focus pricing, supplier negotiation, and portfolio strategy on the specific products and divisions shown here to matter most.

---

## 🚀 Future Work

- Add regional profitability deep-dive across Interior, Atlantic, Gulf, and Pacific markets
- Integrate live data via database connection or REST API
- Build predictive margin forecasting using regression models
- Deploy the app publicly via Streamlit Community Cloud
- Add automated PDF report generation for non-technical stakeholders

---

## 👤 Author & Contact

**Mohammed Ashif Maniyar**
Data Analytics Intern — Unified Mentor, Haryana, India

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/mohammed-ashif-maniyar-95b347152)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://https://github.com/MdashifManiyar/nassau_candy-profitability_and_margin_performance_analysis)
[![Email](https://img.shields.io/badge/Email-Contact-red?logo=gmail)](mailto:mdasifmaniyar73@gmail.com)

> *Built as part of a 3-month Data Analytics internship at Unified Mentor — demonstrating end-to-end skills in data cleaning, EDA, KPI design, dashboard development, and business storytelling.*
