# ──────────────────────────────────────
# Imports
# ──────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ──────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy Dashboard",
    page_icon="🍬",
    layout="wide"
)

# ──────────────────────────────────────
# Custom Styling
# ──────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}

    .stApp {
        background-color: #f8f9fb;
    }

    section[data-testid="stSidebar"] {
        background-color: #1a2942;
    }
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    h1 {
        color: #1a2942;
        border-bottom: 3px solid #c9971f;
        padding-bottom: 10px;
    }
    h2 {
        color: #1a2942;
        margin-top: 1.5rem;
    }
    h3 {
        color: #374151;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #c9971f;
        border-radius: 10px;
        padding: 14px 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
        min-height: 100px;
    }
    div[data-testid="stMetricLabel"] {
        color: #6b7280;
    }
    div[data-testid="stMetricValue"] {
        color: #1a2942;
        font-size: 26px;
        white-space: normal;
        line-height: 1.3;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: transparent;
        color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a2942;
        color: #ffffff !important;
    }

    .stButton button {
        background-color: #1a2942;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
    }
    .stButton button:hover {
        background-color: #c9971f;
        color: #1a2942;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        overflow: hidden;
    }
    hr {
        margin: 1.5rem 0;
        border-color: #e5e7eb;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #1a2942 !important;
    }
    section[data-testid="stSidebar"] input {
        color: #1a2942 !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────
# Shared Colors
# ──────────────────────────────────────
DIVISION_COLORS = {"Chocolate": "#8b5cf6", "Sugar": "#f59e0b", "Other": "#06b6d4"}
REFERENCE_LINE_COLOR = "#c9971f"


# ──────────────────────────────────────
# Data Loading
# ──────────────────────────────────────
@st.cache_data
def load_data():
    """Load and prepare the validated Nassau Candy dataset."""
    data = pd.read_csv("Nassau_Candy_Validated.csv")
    data["Order Date"] = pd.to_datetime(data["Order Date"])
    return data


# ──────────────────────────────────────
# Product Metrics Calculation
# ──────────────────────────────────────
@st.cache_data
def get_product_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate product-level KPIs once.
    Used by Tab 1, Tab 3, Tab 4, and Tab 5 so every tab shares one source of truth.
    """
    summary = data.groupby(["Product Name", "Division"]).agg(
        total_sales=("Sales", "sum"),
        total_profit=("Gross Profit", "sum"),
        total_units=("Units", "sum"),
        total_cost=("Cost", "sum")
    ).reset_index()

    summary["gross_margin_pct"] = (summary["total_profit"] / summary["total_sales"] * 100).round(2)
    summary["cost_ratio"] = (summary["total_cost"] / summary["total_sales"]).round(4)
    summary["profit_per_unit"] = (summary["total_profit"] / summary["total_units"]).round(2)
    summary["revenue_contribution_pct"] = (summary["total_sales"] / summary["total_sales"].sum() * 100).round(2)
    summary["profit_contribution_pct"] = (summary["total_profit"] / summary["total_profit"].sum() * 100).round(2)

    # Margin volatility: how much a product's margin swings order to order
    margin_per_order = data.assign(margin=data["Gross Profit"] / data["Sales"])
    volatility = margin_per_order.groupby("Product Name")["margin"].std(ddof=0).round(4)
    summary["margin_volatility"] = summary["Product Name"].map(volatility).fillna(0)

    return summary


df = load_data()

# ──────────────────────────────────────
# Sidebar Branding
# ──────────────────────────────────────
st.sidebar.image("Unified_logo.png", use_container_width=True)
#st.sidebar.markdown("---")
st.sidebar.title("🍬 Nassau Candy")
#st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

# ──────────────────────────────────────
# Filter Widgets
# ──────────────────────────────────────

# Date Range
selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(
        df["Order Date"].min().date(),
        df["Order Date"].max().date()
    ),
    key="date_filter"
)

# Division
selected_divisions = st.sidebar.multiselect(
    "Division",
    options=["Chocolate", "Sugar", "Other"],
    default=["Chocolate", "Sugar", "Other"],
    key="division_filter"
)

# Region
selected_region = st.sidebar.selectbox(
    "Region",
    options=["All", "Interior", "Atlantic", "Gulf", "Pacific"],
    key="region_filter"
)

# Product Search
search_text = st.sidebar.text_input(
    "🔍 Search Product",
    placeholder="e.g. Wonka Bar",
    key="product_search"
)

# Minimum Margin %
min_margin = st.sidebar.slider(
    "Minimum Margin %",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
    key="margin_slider"
)
  
# ──────────────────────────────────────
# Reset Filters
# ──────────────────────────────────────
def reset_filters():
    """Reset every sidebar filter back to its default value."""
    st.session_state["division_filter"] = ["Chocolate", "Sugar", "Other"]
    st.session_state["region_filter"] = "All"
    st.session_state["margin_slider"] = 0
    st.session_state["date_filter"] = (
        df["Order Date"].min().date(),
        df["Order Date"].max().date()
    )
    st.session_state["product_search"] = ""


#st.sidebar.markdown("---")
st.sidebar.button("🔄 Reset All Filters", on_click=reset_filters, use_container_width=True)

# ──────────────────────────────────────
# Apply Filters to Dataset
# ──────────────────────────────────────
filtered_df = df.copy()

if selected_divisions:
    filtered_df = filtered_df[filtered_df["Division"].isin(selected_divisions)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

if search_text:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(search_text, case=False, na=False)
    ]

# ──────────────────────────────────────
# Main Page Logo
# ──────────────────────────────────────
left_col, center_col, right_col = st.columns([1, 2, 1])
with center_col:
    st.image("Nassau_logo.png", use_container_width=True)

st.markdown("---")

# ──────────────────────────────────────
# Tabs
# ──────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Product Profitability",
    "🏭 Division Performance",
    "💰 Cost Diagnostics",
    "📊 Pareto Analysis",
    "🎯 Problem, Solution & Insights"
])

# Shared product-level data used by Tabs 1, 3, 4, 5
product_data = get_product_metrics(filtered_df)

# Apply the Minimum Margin % filter once here — reused by Tabs 1, 3, 4, 5
# (avoids repeating the same filter logic in every tab)
margin_filtered_products = product_data[product_data["gross_margin_pct"] >= min_margin].copy()

    # ──────────────────────────────────────
    # TAB 1
    # ──────────────────────────────────────
with tab1:
    st.header("Product Profitability")
    st.markdown("Gross margin, profit ranking, contribution, and product classification across all products.")

    visible_products = margin_filtered_products

    # ──────────────────────────────────────
    # KPI Cards
    # ──────────────────────────────────────
    st.subheader("Key Metrics")
    total_revenue = filtered_df["Sales"].sum()
    total_profit = filtered_df["Gross Profit"].sum()
    total_units = filtered_df["Units"].sum()

    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    avg_profit_per_unit = (total_profit / total_units) if total_units > 0 else 0
    avg_volatility = visible_products["margin_volatility"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Total Gross Profit", f"${total_profit:,.0f}")
    col3.metric("Avg Gross Margin %", f"{avg_margin:.1f}%")
    col4.metric("Avg Profit / Unit", f"${avg_profit_per_unit:.2f}")
    col5.metric("Avg Margin Volatility", f"{avg_volatility:.4f}")
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Margin Leaderboard
    # ──────────────────────────────────────
    st.subheader("Product Ranking — by Gross Margin %")
    by_margin = visible_products.sort_values("gross_margin_pct", ascending=False)

    margin_chart = px.bar(
        by_margin,
        x="Product Name",
        y="gross_margin_pct",
        color="gross_margin_pct",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        text="gross_margin_pct",
        title="Gross Margin % by Product — Ranked High to Low",
        labels={"gross_margin_pct": "Gross Margin %", "Product Name": ""}
    )
    margin_chart.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    margin_chart.add_hline(
        y=avg_margin, line_dash="dash", line_color=REFERENCE_LINE_COLOR,
        annotation_text=f"Avg: {avg_margin:.1f}%", annotation_position="top right"
    )
    margin_chart.update_layout(
        xaxis_tickangle=-35, coloraxis_showscale=False, height=420, margin=dict(t=50, b=120)
    )
    st.plotly_chart(margin_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Profit Ranking
    # ──────────────────────────────────────
    st.subheader("Product Ranking — by Gross Profit")
    by_profit = visible_products.sort_values("total_profit", ascending=False)

    profit_chart = px.bar(
        by_profit,
        x="Product Name",
        y="total_profit",
        color="gross_margin_pct",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        text="total_profit",
        title="Products Ranked by Gross Profit (color = Margin %)",
        labels={"total_profit": "Gross Profit ($)", "Product Name": ""}
    )
    profit_chart.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    profit_chart.update_layout(
        xaxis_tickangle=-35, height=420, margin=dict(t=50, b=120),
        coloraxis_colorbar_title="Margin %", yaxis_tickprefix="$"
    )
    st.plotly_chart(profit_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Revenue vs Profit Contribution
    # ──────────────────────────────────────
    st.subheader("Profit Contribution vs Revenue Contribution")

    contribution_chart = go.Figure()
    contribution_chart.add_trace(go.Bar(
        name="Revenue Contribution %",
        x=visible_products["Product Name"],
        y=visible_products["revenue_contribution_pct"],
        marker_color="#3b82f6",
        text=visible_products["revenue_contribution_pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside"
    ))
    contribution_chart.add_trace(go.Bar(
        name="Profit Contribution %",
        x=visible_products["Product Name"],
        y=visible_products["profit_contribution_pct"],
        marker_color="#22c55e",
        text=visible_products["profit_contribution_pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside"
    ))
    contribution_chart.update_layout(
        barmode="group",
        title="Revenue Contribution % vs Profit Contribution % — The Gap Tells the Story",
        xaxis_tickangle=-35, height=420, margin=dict(t=50, b=120),
        legend=dict(orientation="h", x=0.6, y=1.1)
    )
    st.plotly_chart(contribution_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Product Classification (3-way)
    # ──────────────────────────────────────
    st.subheader("Product Classification — Sales, Margin & Profit")
    st.caption(
        "High-Profit/High-Margin = winners · High-Sales/Low-Margin = misleading stars · "
        "Low-Sales/Low-Profit = long tail · Mixed = no clear pattern"
    )

    sales_median = visible_products["total_sales"].median()
    margin_median = visible_products["gross_margin_pct"].median()
    profit_median = visible_products["total_profit"].median()

    def classify_product(row):
        is_high_sales = row["total_sales"] >= sales_median
        is_high_margin = row["gross_margin_pct"] >= margin_median
        is_high_profit = row["total_profit"] >= profit_median

        if is_high_profit and is_high_margin:
            return "High-Profit / High-Margin"
        if is_high_sales and not is_high_margin:
            return "High-Sales / Low-Margin"
        if not is_high_sales and not is_high_profit:
            return "Low-Sales / Low-Profit"
        return "Mixed"

    visible_products["category"] = visible_products.apply(classify_product, axis=1)
    category_colors = {
        "High-Profit / High-Margin": "#22c55e",
        "High-Sales / Low-Margin": "#ef4444",
        "Low-Sales / Low-Profit": "#6b7280",
        "Mixed": "#3b82f6"
    }
    category_counts = visible_products["category"].value_counts()

    card1, card2, card3, card4 = st.columns(4)
    card1.success(
        f"⭐ **High-Profit / High-Margin**\n\n"
        f"{category_counts.get('High-Profit / High-Margin', 0)} products\n\n"
        f"Your best performers — protect and grow these."
    )
    card2.error(
        f"⚠ **High-Sales / Low-Margin**\n\n"
        f"{category_counts.get('High-Sales / Low-Margin', 0)} products\n\n"
        f"Misleading 'stars' — sell well but barely profit."
    )
    card3.warning(
        f"📉 **Low-Sales / Low-Profit**\n\n"
        f"{category_counts.get('Low-Sales / Low-Profit', 0)} products\n\n"
        f"Long tail — review for discontinuation."
    )
    card4.info(
        f"➖ **Mixed**\n\n"
        f"{category_counts.get('Mixed', 0)} products\n\n"
        f"Doesn't fit a clear high/low pattern."
    )

    classification_chart = px.scatter(
        visible_products,
        x="total_sales",
        y="gross_margin_pct",
        size="total_profit",
        color="category",
        color_discrete_map=category_colors,
        hover_name="Product Name",
        title="Sales vs Margin — bubble size = Gross Profit",
        labels={"total_sales": "Total Sales ($)", "gross_margin_pct": "Gross Margin %"}
    )
    classification_chart.add_vline(x=sales_median, line_dash="dash", line_color="gray")
    classification_chart.add_hline(y=margin_median, line_dash="dash", line_color="gray")
    classification_chart.update_layout(height=440, margin=dict(t=50, b=40))
    st.plotly_chart(classification_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Full Data Table
    # ──────────────────────────────────────
    st.subheader("Full Product Details Table")

    table = visible_products[[
        "Product Name", "total_sales", "total_profit", "gross_margin_pct",
        "profit_per_unit", "revenue_contribution_pct", "profit_contribution_pct",
        "margin_volatility", "category"
    ]].sort_values("gross_margin_pct", ascending=False)

    table = table.rename(columns={
        "total_sales": "Revenue ($)",
        "total_profit": "Gross Profit ($)",
        "gross_margin_pct": "Gross Margin %",
        "profit_per_unit": "Profit per Unit",
        "revenue_contribution_pct": "Revenue Contribution %",
        "profit_contribution_pct": "Profit Contribution %",
        "margin_volatility": "Margin Volatility",
        "category": "Category"
    })

    table["Revenue ($)"] = table["Revenue ($)"].apply(lambda v: f"${v:,.2f}")
    table["Gross Profit ($)"] = table["Gross Profit ($)"].apply(lambda v: f"${v:,.2f}")
    table["Gross Margin %"] = table["Gross Margin %"].apply(lambda v: f"{v:.1f}%")
    table["Profit per Unit"] = table["Profit per Unit"].apply(lambda v: f"${v:.2f}")
    table["Revenue Contribution %"] = table["Revenue Contribution %"].apply(lambda v: f"{v:.1f}%")
    table["Profit Contribution %"] = table["Profit Contribution %"].apply(lambda v: f"{v:.1f}%")

    st.dataframe(table, use_container_width=True, hide_index=True)

    # ──────────────────────────────────────
    # TAB 2
    # ──────────────────────────────────────
with tab2:
    st.header("Division Performance")
    st.markdown("Revenue, profit, and margin comparison across Chocolate, Sugar, and Other divisions.")

    # ──────────────────────────────────────
    # Division Level Aggregation
    # ──────────────────────────────────────
    division_data = filtered_df.groupby("Division").agg(
        total_sales=("Sales", "sum"),
        total_profit=("Gross Profit", "sum"),
        total_units=("Units", "sum"),
        total_cost=("Cost", "sum"),
        total_orders=("Row ID", "count")
    ).reset_index()

    division_data["avg_margin_pct"] = (division_data["total_profit"] / division_data["total_sales"] * 100).round(2)
    division_data["profit_per_unit"] = (division_data["total_profit"] / division_data["total_units"]).round(2)
    division_data["revenue_share_pct"] = (division_data["total_sales"] / division_data["total_sales"].sum() * 100).round(2)
    division_data["profit_share_pct"] = (division_data["total_profit"] / division_data["total_profit"].sum() * 100).round(2)
    division_data["cost_ratio"] = (division_data["total_cost"] / division_data["total_sales"]).round(4)

    # ──────────────────────────────────────
    # KPI Cards — One per Division
    # ──────────────────────────────────────
    st.subheader("Division KPIs")
    icons = {"Chocolate": "🍫", "Sugar": "🍬", "Other": "🍭"}
    cols = st.columns(3)

    for i, row in division_data.iterrows():
        with cols[i % 3]:
            st.markdown(f"### {icons.get(row['Division'], '📦')} {row['Division']}")
            st.metric("Revenue", f"${row['total_sales']:,.0f}")
            st.metric("Gross Profit", f"${row['total_profit']:,.0f}")
            st.metric("Avg Margin %", f"{row['avg_margin_pct']:.1f}%")
            st.metric("Orders", f"{row['total_orders']:,}")
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Revenue vs Profit by Division
    # ──────────────────────────────────────
    st.subheader("Revenue vs Gross Profit by Division")

    revenue_profit_chart = go.Figure()
    revenue_profit_chart.add_trace(go.Bar(
        name="Total Revenue ($)", x=division_data["Division"], y=division_data["total_sales"],
        marker_color="#3b82f6",
        text=division_data["total_sales"].apply(lambda v: f"${v:,.0f}"), textposition="outside"
    ))
    revenue_profit_chart.add_trace(go.Bar(
        name="Gross Profit ($)", x=division_data["Division"], y=division_data["total_profit"],
        marker_color="#22c55e",
        text=division_data["total_profit"].apply(lambda v: f"${v:,.0f}"), textposition="outside"
    ))
    revenue_profit_chart.update_layout(
        barmode="group", title="Revenue vs Gross Profit — Division Comparison",
        height=420, margin=dict(t=50, b=60), legend=dict(orientation="h", x=0.7, y=1.1),
        yaxis_title="Amount ($)", yaxis_tickprefix="$"
    )
    st.plotly_chart(revenue_profit_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Average Margin % by Division
    # ──────────────────────────────────────
    st.subheader("Average Gross Margin % by Division")

    overall_avg_margin = (
        filtered_df["Gross Profit"].sum() / filtered_df["Sales"].sum() * 100
        if filtered_df["Sales"].sum() > 0 else 0
    )

    margin_by_division_chart = px.bar(
        division_data.sort_values("avg_margin_pct", ascending=False),
        x="Division", y="avg_margin_pct", color="avg_margin_pct",
        color_continuous_scale="RdYlGn", range_color=[0, 100], text="avg_margin_pct",
        title="Which Division is Most Profitable per Dollar of Revenue?",
        labels={"avg_margin_pct": "Avg Gross Margin %"}
    )
    margin_by_division_chart.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    margin_by_division_chart.add_hline(
        y=overall_avg_margin, line_dash="dash", line_color=REFERENCE_LINE_COLOR,
        annotation_text=f"Overall Avg: {overall_avg_margin:.1f}%", annotation_position="top right"
    )
    margin_by_division_chart.update_layout(coloraxis_showscale=False, height=400, margin=dict(t=50, b=60))
    st.plotly_chart(margin_by_division_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Top Products per Division
    # ──────────────────────────────────────
    st.subheader("Top Products within Each Division")

    product_by_division = filtered_df.groupby(["Division", "Product Name"]).agg(
        sales=("Sales", "sum"), profit=("Gross Profit", "sum"), units=("Units", "sum")
    ).reset_index()
    product_by_division["margin_pct"] = (product_by_division["profit"] / product_by_division["sales"] * 100).round(2)

    top_products = (
        product_by_division.sort_values("profit", ascending=False)
        .groupby("Division").head(3).reset_index(drop=True)
    )

    top_products_chart = px.bar(
        top_products.sort_values("profit", ascending=True),
        x="profit", y="Product Name", color="Division",
        color_discrete_map=DIVISION_COLORS, orientation="h", text="margin_pct",
        title="Top 3 Products per Division — by Gross Profit",
        labels={"profit": "Gross Profit ($)", "Product Name": ""}
    )
    top_products_chart.update_traces(texttemplate="%{text:.1f}% margin", textposition="outside")
    top_products_chart.update_layout(height=420, margin=dict(t=50, b=60, r=120), legend_title="Division")
    st.plotly_chart(top_products_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Division Summary Table
    # ──────────────────────────────────────
    st.subheader("Division Summary Table")

    division_table = division_data[[
        "Division", "total_sales", "total_profit", "avg_margin_pct",
        "profit_per_unit", "revenue_share_pct", "profit_share_pct", "total_orders"
    ]].rename(columns={
        "total_sales": "Revenue ($)", "total_profit": "Gross Profit ($)",
        "avg_margin_pct": "Avg Margin %", "profit_per_unit": "Profit per Unit",
        "revenue_share_pct": "Revenue Share %", "profit_share_pct": "Profit Share %",
        "total_orders": "Orders"
    })

    division_table["Revenue ($)"] = division_table["Revenue ($)"].apply(lambda v: f"${v:,.2f}")
    division_table["Gross Profit ($)"] = division_table["Gross Profit ($)"].apply(lambda v: f"${v:,.2f}")
    division_table["Avg Margin %"] = division_table["Avg Margin %"].apply(lambda v: f"{v:.1f}%")
    division_table["Profit per Unit"] = division_table["Profit per Unit"].apply(lambda v: f"${v:.2f}")
    division_table["Revenue Share %"] = division_table["Revenue Share %"].apply(lambda v: f"{v:.1f}%")
    division_table["Profit Share %"] = division_table["Profit Share %"].apply(lambda v: f"{v:.1f}%")

    st.dataframe(division_table, use_container_width=True, hide_index=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Division Efficiency Classification
    # ──────────────────────────────────────
    st.subheader("Division Classification — Efficiency vs Structural Issues")

    for _, row in division_data.iterrows():
        if row["avg_margin_pct"] >= overall_avg_margin:
            st.success(
                f"✓ **{row['Division']}** — Strong financial efficiency "
                f"(Margin: {row['avg_margin_pct']:.1f}% vs overall {overall_avg_margin:.1f}%, "
                f"Cost Ratio: {row['cost_ratio']:.2f})"
            )
        else:
            st.error(
                f"⚠ **{row['Division']}** — Structural margin issue "
                f"(Margin: {row['avg_margin_pct']:.1f}% — below overall {overall_avg_margin:.1f}%, "
                f"Cost Ratio: {row['cost_ratio']:.2f})"
            )
    st.markdown("---")

    # ──────────────────────────────────────
    # Key Insight
    # ──────────────────────────────────────
    st.subheader("Key Insight")

    if "Chocolate" in division_data["Division"].values:
        choc = division_data[division_data["Division"] == "Chocolate"].iloc[0]
        sugar_orders = division_data.loc[division_data["Division"] == "Sugar", "total_orders"]
        sugar_orders_text = f"{sugar_orders.iloc[0]}" if len(sugar_orders) > 0 else "N/A"
        st.warning(
            f"⚠ Chocolate division dominates with **{choc['revenue_share_pct']:.1f}% of revenue** "
            f"and **{choc['profit_share_pct']:.1f}% of profit** — heavy concentration risk. "
            f"Sugar division has critically low volume ({sugar_orders_text} orders only)."
        )

    # ──────────────────────────────────────
    # TAB 3
    # ──────────────────────────────────────
with tab3:
    st.header("Cost Diagnostics")
    st.markdown("Cost vs sales analysis, margin risk classification, and products flagged for action.")

    cost_data = margin_filtered_products.copy()

    # ──────────────────────────────────────
    # Risk Classification
    # ──────────────────────────────────────
    def classify_risk(row):
        if row["cost_ratio"] < 0.4 and row["gross_margin_pct"] > 60:
            return "Star"
        if row["cost_ratio"] >= 0.4 and row["gross_margin_pct"] > 60:
            return "Reprice"
        if row["cost_ratio"] < 0.4 and row["gross_margin_pct"] <= 60:
            return "Volume Play"
        return "Discontinue"

    cost_data["risk_quadrant"] = cost_data.apply(classify_risk, axis=1)

    action_map = {
        "Star": "Maintain — No Change Needed",
        "Reprice": "Cost Renegotiation",
        "Volume Play": "Maintain — Scale Volume",
        "Discontinue": "Repricing / Discontinuation Review"
    }
    cost_data["recommended_action"] = cost_data["risk_quadrant"].map(action_map)

    # ──────────────────────────────────────
    # KPI Cards
    # ──────────────────────────────────────
    st.subheader("Cost Risk Summary")

    total_cost = filtered_df["Cost"].sum()
    avg_cost_ratio = (filtered_df["Cost"].sum() / filtered_df["Sales"].sum()) if filtered_df["Sales"].sum() > 0 else 0
    star_count = (cost_data["risk_quadrant"] == "Star").sum()
    discontinue_count = (cost_data["risk_quadrant"] == "Discontinue").sum()
    reprice_count = (cost_data["risk_quadrant"] == "Reprice").sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Cost", f"${total_cost:,.0f}")
    col2.metric("Avg Cost Ratio", f"{avg_cost_ratio:.1%}")
    col3.metric("⭐ Stars", f"{star_count}", help="Products in good standing")
    col4.metric("⚠ Discontinue", f"{discontinue_count}", help="High cost, low margin")
    col5.metric("🔄 Reprice", f"{reprice_count}", help="High cost, high margin")
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Raw Cost vs Sales
    # ──────────────────────────────────────
    st.subheader("Cost vs Sales — Raw Scatter Analysis")

    cost_vs_sales_chart = px.scatter(
        cost_data, x="total_sales", y="total_cost", color="Division",
        color_discrete_map=DIVISION_COLORS, size="total_profit", hover_name="Product Name",
        title="Cost vs Sales — Each Point = 1 Product",
        labels={"total_sales": "Sales ($)", "total_cost": "Cost ($)"}
    )
    if len(cost_data) > 0:
        max_value = max(cost_data["total_sales"].max(), cost_data["total_cost"].max())
        cost_vs_sales_chart.add_shape(
            type="line", x0=0, y0=0, x1=max_value, y1=max_value * 0.4,
            line=dict(color="gray", dash="dash", width=1)
        )
        cost_vs_sales_chart.add_annotation(
            x=max_value * 0.9, y=max_value * 0.36, text="40% cost-to-sales line",
            showarrow=False, font=dict(size=10, color="gray")
        )
    cost_vs_sales_chart.update_layout(height=420, margin=dict(t=50, b=40), xaxis_tickprefix="$", yaxis_tickprefix="$")
    st.plotly_chart(cost_vs_sales_chart, use_container_width=True)
    st.caption("Products above the dashed line spend more than 40% of revenue on cost — flagged below.")
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Cost Ratio vs Margin (Risk Diagnostic)
    # ──────────────────────────────────────
    st.subheader("Cost Ratio vs Gross Margin % — Risk Diagnostic")

    risk_colors = {"Star": "#22c55e", "Reprice": "#f59e0b", "Volume Play": "#3b82f6", "Discontinue": "#ef4444"}

    risk_chart = px.scatter(
        cost_data, x="cost_ratio", y="gross_margin_pct", color="risk_quadrant",
        color_discrete_map=risk_colors, size="total_sales", hover_name="Product Name",
        hover_data={"Division": True, "cost_ratio": ":.2f", "gross_margin_pct": ":.1f",
                    "total_sales": ":,.0f", "risk_quadrant": False},
        title="Cost Ratio vs Gross Margin % — Each Bubble = 1 Product (Size = Revenue)",
        labels={"cost_ratio": "Cost Ratio (Cost / Sales)", "gross_margin_pct": "Gross Margin %"}
    )
    risk_chart.add_vline(x=0.4, line_dash="dash", line_color="gray",
                          annotation_text="Cost threshold: 0.4", annotation_position="top")
    risk_chart.add_hline(y=60, line_dash="dash", line_color="gray",
                          annotation_text="Margin threshold: 60%", annotation_position="right")
    risk_chart.add_annotation(x=0.15, y=85, text="⭐ Stars", showarrow=False, font=dict(color="#22c55e", size=12))
    risk_chart.add_annotation(x=0.65, y=85, text="🔄 Reprice", showarrow=False, font=dict(color="#f59e0b", size=12))
    risk_chart.add_annotation(x=0.15, y=20, text="📦 Volume Play", showarrow=False, font=dict(color="#3b82f6", size=12))
    risk_chart.add_annotation(x=0.65, y=20, text="❌ Discontinue", showarrow=False, font=dict(color="#ef4444", size=12))
    risk_chart.update_layout(height=480, margin=dict(t=60, b=60))
    st.plotly_chart(risk_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # 2x2 Risk Matrix
    # ──────────────────────────────────────
    st.subheader("2×2 Risk Classification Matrix")

    quadrant_counts = cost_data["risk_quadrant"].value_counts().to_dict()
    col_left, col_right = st.columns(2)

    with col_left:
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)
        r1c1.success(f"⭐ **Stars**\n\n**{quadrant_counts.get('Star', 0)} products**\n\nLow cost · High margin\n\nAction: Maintain")
        r1c2.warning(f"🔄 **Reprice**\n\n**{quadrant_counts.get('Reprice', 0)} products**\n\nHigh cost · High margin\n\nAction: Cost Renegotiation")
        r2c1.info(f"📦 **Volume Play**\n\n**{quadrant_counts.get('Volume Play', 0)} products**\n\nLow cost · Low margin\n\nAction: Scale Volume")
        r2c2.error(f"❌ **Discontinue**\n\n**{quadrant_counts.get('Discontinue', 0)} products**\n\nHigh cost · Low margin\n\nAction: Repricing / Discontinuation Review")

    with col_right:
        risk_pie = px.pie(
            names=list(quadrant_counts.keys()), values=list(quadrant_counts.values()),
            color=list(quadrant_counts.keys()), color_discrete_map=risk_colors,
            title="Risk Distribution", hole=0.5
        )
        risk_pie.update_traces(textinfo="label+percent", textposition="outside")
        risk_pie.update_layout(height=320, margin=dict(t=50, b=20), showlegend=False)
        st.plotly_chart(risk_pie, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Flagged Products Table
    # ──────────────────────────────────────
    st.subheader("Products Flagged for Action")

    flagged_products = cost_data[
        cost_data["risk_quadrant"].isin(["Discontinue", "Reprice"])
    ].sort_values("cost_ratio", ascending=False)

    if len(flagged_products) > 0:
        flagged_table = flagged_products[[
            "Product Name", "Division", "total_sales", "total_cost",
            "gross_margin_pct", "cost_ratio", "risk_quadrant", "recommended_action"
        ]].rename(columns={
            "total_sales": "Revenue ($)", "total_cost": "Cost ($)",
            "gross_margin_pct": "Gross Margin %", "cost_ratio": "Cost Ratio",
            "risk_quadrant": "Risk Quadrant", "recommended_action": "Recommended Action"
        })
        flagged_table["Revenue ($)"] = flagged_table["Revenue ($)"].apply(lambda v: f"${v:,.2f}")
        flagged_table["Cost ($)"] = flagged_table["Cost ($)"].apply(lambda v: f"${v:,.2f}")
        flagged_table["Gross Margin %"] = flagged_table["Gross Margin %"].apply(lambda v: f"{v:.1f}%")
        flagged_table["Cost Ratio"] = flagged_table["Cost Ratio"].apply(lambda v: f"{v:.2f}")
        st.dataframe(flagged_table, use_container_width=True, hide_index=True)
    else:
        st.success("No products flagged for action!")
    st.markdown("---")

    # ──────────────────────────────────────
    # Key Insights
    # ──────────────────────────────────────
    st.subheader("Key Insights")

    if len(cost_data) > 0:
        worst_product = cost_data.sort_values("cost_ratio", ascending=False).iloc[0]
        best_product = cost_data.sort_values("gross_margin_pct", ascending=False).iloc[0]

        col1, col2 = st.columns(2)
        col1.error(
            f"❌ **Highest Risk Product**\n\n**{worst_product['Product Name']}** — "
            f"Cost Ratio: {worst_product['cost_ratio']:.2f} | Margin: {worst_product['gross_margin_pct']:.1f}% | "
            f"{worst_product['Division']} | Action: {worst_product['recommended_action']}"
        )
        col2.success(
            f"⭐ **Best Performing Product**\n\n**{best_product['Product Name']}** — "
            f"Margin: {best_product['gross_margin_pct']:.1f}% | Cost Ratio: {best_product['cost_ratio']:.2f} | "
            f"{best_product['Division']}"
        )
    # ──────────────────────────────────────
    # TAB 4
    # ──────────────────────────────────────
with tab4:
    st.header("Pareto Analysis")
    st.markdown("Which products drive 80% of revenue and profit? Identify the vital few vs the trivial many.")

    # ──────────────────────────────────────
    # Pareto Base Data
    # ──────────────────────────────────────
    pareto_data = margin_filtered_products[
        ["Product Name", "total_sales", "total_profit"]
    ].copy()

    total_profit_sum = pareto_data["total_profit"].sum()
    total_revenue_sum = pareto_data["total_sales"].sum()
    pareto_data["profit_contribution_pct"] = (pareto_data["total_profit"] / total_profit_sum * 100).round(2)
    pareto_data["revenue_contribution_pct"] = (pareto_data["total_sales"] / total_revenue_sum * 100).round(2)

    profit_ranked = pareto_data.sort_values("total_profit", ascending=False).reset_index(drop=True)
    profit_ranked["rank"] = profit_ranked.index + 1
    profit_ranked["cumulative_profit_pct"] = profit_ranked["profit_contribution_pct"].cumsum().round(2)

    revenue_ranked = pareto_data.sort_values("total_sales", ascending=False).reset_index(drop=True)
    revenue_ranked["rank"] = revenue_ranked.index + 1
    revenue_ranked["cumulative_revenue_pct"] = revenue_ranked["revenue_contribution_pct"].cumsum().round(2)

    top80_profit = profit_ranked[profit_ranked["cumulative_profit_pct"] <= 80]
    top80_revenue = revenue_ranked[revenue_ranked["cumulative_revenue_pct"] <= 80]

    # ──────────────────────────────────────
    # KPI Cards
    # ──────────────────────────────────────
    st.subheader("Concentration Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Products", f"{len(pareto_data)}")
    col2.metric(
        "Products → 80% Profit", f"{len(top80_profit)}",
        help=f"{len(top80_profit) / len(pareto_data) * 100:.0f}% of catalog" if len(pareto_data) else ""
    )
    col3.metric(
        "Products → 80% Revenue", f"{len(top80_revenue)}",
        help=f"{len(top80_revenue) / len(pareto_data) * 100:.0f}% of catalog" if len(pareto_data) else ""
    )
    if len(profit_ranked) > 0:
        col4.metric(
            "Top 1 Product Profit Share",
            f"{profit_ranked.iloc[0]['profit_contribution_pct']:.1f}%",
            help=profit_ranked.iloc[0]["Product Name"]
        )
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Profit Pareto
    # ──────────────────────────────────────
    st.subheader("Pareto Chart — Profit Concentration")

    profit_pareto_chart = go.Figure()
    profit_pareto_chart.add_trace(go.Bar(
        x=profit_ranked["Product Name"], y=profit_ranked["total_profit"], name="Gross Profit ($)",
        marker_color="#22c55e", yaxis="y1",
        text=profit_ranked["profit_contribution_pct"].apply(lambda v: f"{v:.1f}%"), textposition="outside"
    ))
    profit_pareto_chart.add_trace(go.Scatter(
        x=profit_ranked["Product Name"], y=profit_ranked["cumulative_profit_pct"], name="Cumulative Profit %",
        mode="lines+markers+text", line=dict(color="#f59e0b", width=2.5), marker=dict(size=7), yaxis="y2",
        text=profit_ranked["cumulative_profit_pct"].apply(lambda v: f"{v:.0f}%"),
        textposition="top center", textfont=dict(size=10)
    ))
    profit_pareto_chart.add_hline(
        y=80, line_dash="dash", line_color=REFERENCE_LINE_COLOR, line_width=1.5,
        annotation_text="80% threshold", annotation_position="top right", yref="y2"
    )
    profit_pareto_chart.update_layout(
        title=f"Profit Pareto — Top {len(top80_profit)} products drive 80% of total profit",
        xaxis=dict(tickangle=-35, title=""), yaxis=dict(title="Gross Profit ($)", showgrid=False),
        yaxis2=dict(title="Cumulative Profit %", overlaying="y", side="right", range=[0, 110],
                    showgrid=False, ticksuffix="%"),
        legend=dict(orientation="h", x=0.7, y=1.12), height=480, margin=dict(t=80, b=120), yaxis_tickprefix="$"
    )
    st.plotly_chart(profit_pareto_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Chart: Revenue Pareto
    # ──────────────────────────────────────
    st.subheader("Pareto Chart — Revenue Concentration")

    revenue_pareto_chart = go.Figure()
    revenue_pareto_chart.add_trace(go.Bar(
        x=revenue_ranked["Product Name"], y=revenue_ranked["total_sales"], name="Revenue ($)",
        marker_color="#3b82f6", yaxis="y1",
        text=revenue_ranked["revenue_contribution_pct"].apply(lambda v: f"{v:.1f}%"), textposition="outside"
    ))
    revenue_pareto_chart.add_trace(go.Scatter(
        x=revenue_ranked["Product Name"], y=revenue_ranked["cumulative_revenue_pct"], name="Cumulative Revenue %",
        mode="lines+markers+text", line=dict(color="#f59e0b", width=2.5), marker=dict(size=7), yaxis="y2",
        text=revenue_ranked["cumulative_revenue_pct"].apply(lambda v: f"{v:.0f}%"),
        textposition="top center", textfont=dict(size=10)
    ))
    revenue_pareto_chart.add_hline(
        y=80, line_dash="dash", line_color=REFERENCE_LINE_COLOR, line_width=1.5,
        annotation_text="80% threshold", annotation_position="top right", yref="y2"
    )
    revenue_pareto_chart.update_layout(
        title=f"Revenue Pareto — Top {len(top80_revenue)} products drive 80% of total revenue",
        xaxis=dict(tickangle=-35, title=""), yaxis=dict(title="Revenue ($)", showgrid=False),
        yaxis2=dict(title="Cumulative Revenue %", overlaying="y", side="right", range=[0, 110],
                    showgrid=False, ticksuffix="%"),
        legend=dict(orientation="h", x=0.7, y=1.12), height=480, margin=dict(t=80, b=120), yaxis_tickprefix="$"
    )
    st.plotly_chart(revenue_pareto_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Over-Dependency Risk Indicator
    # ──────────────────────────────────────
    st.subheader("Over-Dependency Risk Indicator")

    if len(profit_ranked) > 0:
        top1_share = profit_ranked.iloc[0]["profit_contribution_pct"]
        top3_share = profit_ranked.head(3)["profit_contribution_pct"].sum()
        top5_share = profit_ranked.head(5)["profit_contribution_pct"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Top 1 — Profit Share", f"{top1_share:.1f}%", help=profit_ranked.iloc[0]["Product Name"])
        col2.metric("Top 3 — Profit Share", f"{top3_share:.1f}%")
        col3.metric("Top 5 — Profit Share", f"{top5_share:.1f}%")

        if top3_share > 70:
            st.error(f"🚨 **Critical Dependency Risk** — Top 3 products alone contribute **{top3_share:.1f}%** of total profit.")
        elif top3_share > 50:
            st.warning(f"⚠ **High Concentration Risk** — Top 3 products contribute **{top3_share:.1f}%** of total profit.")
        else:
            st.success("✓ Profit is well distributed across products.")
    st.markdown("---")

    # ──────────────────────────────────────
    # Full Pareto Table
    # ──────────────────────────────────────
    st.subheader("Full Pareto Table — Profit Ranked")

    pareto_table = profit_ranked[[
        "rank", "Product Name", "total_sales", "total_profit",
        "profit_contribution_pct", "cumulative_profit_pct"
    ]].rename(columns={
        "rank": "Profit Rank", "total_sales": "Revenue ($)", "total_profit": "Gross Profit ($)",
        "profit_contribution_pct": "Profit Contribution %", "cumulative_profit_pct": "Cumulative Profit %"
    })
    pareto_table["Revenue ($)"] = pareto_table["Revenue ($)"].apply(lambda v: f"${v:,.2f}")
    pareto_table["Gross Profit ($)"] = pareto_table["Gross Profit ($)"].apply(lambda v: f"${v:,.2f}")
    pareto_table["Profit Contribution %"] = pareto_table["Profit Contribution %"].apply(lambda v: f"{v:.2f}%")
    pareto_table["Cumulative Profit %"] = pareto_table["Cumulative Profit %"].apply(lambda v: f"{v:.2f}%")
    st.dataframe(pareto_table, use_container_width=True, hide_index=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Key Takeaway
    # ──────────────────────────────────────
    st.subheader("Key Takeaway")
    if len(pareto_data) > 0:
        st.info(
            f"📌 **{len(top80_profit)} out of {len(pareto_data)} products "
            f"({len(top80_profit) / len(pareto_data) * 100:.0f}% of catalog) generate 80% of total profit.** "
            f"Strategic focus, inventory priority, and marketing investment should center on these products."
        )

    # ──────────────────────────────────────
    # TAB 5
    # ──────────────────────────────────────
with tab5:
    st.header("Problem, Solution & Insights")
    st.markdown(
        "Currently, the organization lacks visibility into key profitability drivers. "
        "This section answers each core business question using the data analyzed across this dashboard."
    )
    st.markdown("---")

    # ──────────────────────────────────────
    # Supporting Data
    # ──────────────────────────────────────
    insight_products = margin_filtered_products

    insight_divisions = filtered_df.groupby("Division").agg(
        total_sales=("Sales", "sum"), total_profit=("Gross Profit", "sum")
    ).reset_index()
    insight_divisions["margin_pct"] = (insight_divisions["total_profit"] / insight_divisions["total_sales"] * 100).round(2)

    sales_median = insight_products["total_sales"].median()
    margin_median = insight_products["gross_margin_pct"].median()

    # ──────────────────────────────────────
    # Question 1 — Highest Gross Margin
    # ──────────────────────────────────────
    st.subheader("1️⃣ Which product lines deliver the highest gross margin?")

    top3 = insight_products.sort_values("gross_margin_pct", ascending=False).head(3)
    if len(top3) >= 3:
        st.markdown(f"""
**Problem:** Leadership had no clear ranking of which products generate the strongest margins.

**Solution:** Every product's Gross Margin % was calculated and ranked highest to lowest.

**Insight:** Top 3 margin performers: **{top3.iloc[0]['Product Name']}** ({top3.iloc[0]['gross_margin_pct']:.1f}%), 
**{top3.iloc[1]['Product Name']}** ({top3.iloc[1]['gross_margin_pct']:.1f}%), 
**{top3.iloc[2]['Product Name']}** ({top3.iloc[2]['gross_margin_pct']:.1f}%).
""")
        top3_chart = px.bar(
            top3, x="Product Name", y="gross_margin_pct", color="gross_margin_pct",
            color_continuous_scale="RdYlGn", range_color=[0, 100], text="gross_margin_pct",
            title="Top 3 Highest Margin Products"
        )
        top3_chart.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        top3_chart.update_layout(height=350, coloraxis_showscale=False, margin=dict(t=50, b=40))
        st.plotly_chart(top3_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Question 2 — High Sales vs Profitability
    # ──────────────────────────────────────
    st.subheader("2️⃣ Whether high-sales products are actually profitable?")

    risky_products = insight_products[
        (insight_products["total_sales"] >= sales_median) &
        (insight_products["gross_margin_pct"] < margin_median)
    ].sort_values("total_sales", ascending=False)

    st.markdown("""
**Problem:** High sales volume was assumed to mean high profitability — never verified.

**Solution:** Each product's Sales volume was compared against its Gross Margin %.
""")

    if len(risky_products) > 0:
        names = ", ".join(risky_products["Product Name"].tolist())
        st.markdown(f"**Insight:** No — high sales don't guarantee profit. **{names}** sell well but sit below median margin.")

        risky_chart = go.Figure()
        risky_chart.add_trace(go.Bar(
            x=risky_products["Product Name"], y=risky_products["total_sales"],
            name="Sales ($)", marker_color="#3b82f6", yaxis="y1"
        ))
        risky_chart.add_trace(go.Scatter(
            x=risky_products["Product Name"], y=risky_products["gross_margin_pct"],
            name="Margin %", mode="markers+lines",
            marker=dict(color="#ef4444", size=10), line=dict(color="#ef4444"), yaxis="y2"
        ))
        risky_chart.update_layout(
            title="High-Sales but Low-Margin Products — The Hidden Risk",
            yaxis=dict(title="Sales ($)", tickprefix="$", showgrid=False),
            yaxis2=dict(title="Margin %", overlaying="y", side="right", ticksuffix="%", showgrid=False),
            height=380, margin=dict(t=50, b=60), legend=dict(orientation="h", x=0.8, y=1.12)
        )
        st.plotly_chart(risky_chart, use_container_width=True)
    else:
        st.success("**Insight:** No high-sales/low-margin risk products at the current filter level.")
    st.markdown("---")

    # ──────────────────────────────────────
    # Question 3 — Division Profitability
    # ──────────────────────────────────────
    st.subheader("3️⃣ How profitability varies across product divisions?")

    if len(insight_divisions) > 0:
        best_division = insight_divisions.sort_values("margin_pct", ascending=False).iloc[0]
        worst_division = insight_divisions.sort_values("margin_pct", ascending=True).iloc[0]

        st.markdown(f"""
**Problem:** Profitability was tracked company-wide only, hiding division-level differences.

**Solution:** Revenue, profit, and margin compared side-by-side per division.

**Insight:** **{best_division['Division']}** leads at {best_division['margin_pct']:.1f}% margin; 
**{worst_division['Division']}** trails at {worst_division['margin_pct']:.1f}% — a 
{best_division['margin_pct'] - worst_division['margin_pct']:.1f}-point gap, suggesting a structural 
cost issue in {worst_division['Division']}.
""")
        division_margin_chart = px.bar(
            insight_divisions.sort_values("margin_pct", ascending=False),
            x="Division", y="margin_pct", color="margin_pct",
            color_continuous_scale="RdYlGn", range_color=[0, 100], text="margin_pct",
            title="Gross Margin % by Division"
        )
        division_margin_chart.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        division_margin_chart.update_layout(height=350, coloraxis_showscale=False, margin=dict(t=50, b=40))
        st.plotly_chart(division_margin_chart, use_container_width=True)
    st.markdown("---")

    # ──────────────────────────────────────
    # Question 4 — Margin Risk Products
    # ──────────────────────────────────────
    st.subheader("4️⃣ Which products represent margin risk?")

    margin_risk_products = insight_products[
        (insight_products["cost_ratio"] >= 0.4) & (insight_products["gross_margin_pct"] <= 60)
    ].sort_values("cost_ratio", ascending=False)

    st.markdown("""
**Problem:** No systematic way existed to flag products where rising cost quietly erodes margin.

**Solution:** Cost Ratio plotted against Gross Margin %; high-cost/low-margin products flagged for action.
""")

    if len(margin_risk_products) > 0:
        worst_risk = margin_risk_products.iloc[0]
        st.markdown(
            f"**Insight:** **{len(margin_risk_products)} products** are in the margin-risk zone. "
            f"Most severe: **{worst_risk['Product Name']}** "
            f"(Cost Ratio {worst_risk['cost_ratio']:.2f}, Margin {worst_risk['gross_margin_pct']:.1f}%)."
        )
        margin_risk_chart = px.scatter(
            margin_risk_products, x="cost_ratio", y="gross_margin_pct", size="total_sales",
            color="gross_margin_pct", color_continuous_scale="RdYlGn", hover_name="Product Name",
            title="Margin Risk Products — High Cost Ratio, Low Margin"
        )
        margin_risk_chart.update_layout(height=400, margin=dict(t=50, b=40))
        st.plotly_chart(margin_risk_chart, use_container_width=True)
        st.dataframe(
            margin_risk_products[["Product Name", "cost_ratio", "gross_margin_pct"]].rename(
                columns={"cost_ratio": "Cost Ratio", "gross_margin_pct": "Margin %"}
            ),
            use_container_width=True, hide_index=True
        )
    else:
        st.success("**Insight:** No margin-risk products at the current filter level.")
    st.markdown("---")

    # ──────────────────────────────────────
    # Executive Summary
    # ──────────────────────────────────────
    st.subheader("Executive Summary")
    worst_name = worst_division["Division"] if len(insight_divisions) > 0 else "a division"
    risk_count = len(margin_risk_products)
    st.info(
        f"Nassau Candy's profitability is concentrated in a few high-margin products, while "
        f"{worst_name} and a handful of high-sales/low-margin products quietly erode returns. "
        f"Addressing the {risk_count} flagged margin-risk products is the clearest path to "
        f"improving profitability without sacrificing revenue."
    )