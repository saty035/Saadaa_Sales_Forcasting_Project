
import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="📊 SAADAA's Sales Forecasting, Vendor Allocation & Fabric Utilization Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Header ----
st.title("📊 SAADAA's Sales Forecasting, Vendor Allocation & Fabric Utilization Dashboard")

# ---- Data Loading Function ----
@st.cache_data
def load_data(path, parse_dates=None):
    """
    Load CSV data with optional date parsing for date columns.
    """
    return pd.read_csv(path, parse_dates=parse_dates)

# ---- Load Datasets ----
forecasts = load_data("prediction_data/next_30_day_forecast.csv", parse_dates=["Date"])
alloc_df = load_data("prediction_data/final_allocation.csv")
fabric_summary = load_data("prediction_data/filtered_fabric_summary.csv")

# Drop any unwanted columns
alloc_df = alloc_df.drop(columns=[c for c in ["Unnamed: 0", "Max_Supply"] if c in alloc_df.columns])
fabric_summary = fabric_summary.drop(columns=[c for c in ["Unnamed: 0"] if c in fabric_summary.columns])

# ---- Sidebar Intro ----
st.sidebar.markdown(
    """
    <h2>🎯 Target your view!</h2>
    <p>Choose the SKU(s) and vendor(s) you want to analyze.</p>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# ---- Sidebar Filters ----
st.sidebar.header("Filters")
# SKU multi-select
sku_list = sorted(forecasts["SKU"].unique())
selected_skus = st.sidebar.multiselect("SKU(s)", sku_list, default=sku_list)
# Vendor multi-select
vendor_list = sorted(alloc_df["Vendor"].unique())
selected_vendors = st.sidebar.multiselect("Vendor(s)", vendor_list, default=vendor_list)

# ---- Apply Allocation & Fabric Filters ----
df_alloc = alloc_df[
    alloc_df["SKU"].isin(selected_skus)
    & alloc_df["Vendor"].isin(selected_vendors)
]
mask_vendor = fabric_summary["Vendor"].isin(selected_vendors)
mask_sku = fabric_summary["SKUs"].str.split(", ").apply(
    lambda lst: any(sku in lst for sku in selected_skus)
)
df_fab = fabric_summary[mask_vendor & mask_sku]

# ---- Tab Layout ----
tabs = st.tabs(["📈 Forecast", "📊 Allocations", "🧵 Fabric Usage", "💡 Recommendations"])

# ----- Forecast Tab -----
with tabs[0]:
    st.markdown("## 30-Day SKU Forecast")
    # Date range selector
    min_date = forecasts["Date"].min()
    max_date = forecasts["Date"].max()
    start_date, end_date = st.date_input(
        "Select Forecast Date Range", [min_date, max_date],
        min_value=min_date, max_value=max_date
    )
    if start_date > end_date:
        st.error("Start date must be before or equal to end date.")
    else:
        df_fore = forecasts[
            forecasts["SKU"].isin(selected_skus)
            & (forecasts["Date"] >= pd.to_datetime(start_date))
            & (forecasts["Date"] <= pd.to_datetime(end_date))
        ]
        # Plot forecast
        fig_f = px.line(
            df_fore, x="Date", y="Forecast_Units", color="SKU",
            markers=True, title="Forecast Units Over Time", height=400
        )
        fig_f.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_f, use_container_width=True)
        # Data table + download
        with st.expander("Show forecast data", expanded=True):
            st.dataframe(df_fore, use_container_width=True)
            csv = df_fore.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Forecast Data", csv, "filtered_forecast.csv", "text/csv")

# ----- Allocations Tab -----
with tabs[1]:
    st.markdown("## Vendor Allocation Suggestions")
    fig_a = px.bar(
        df_alloc, x="Vendor", y="Allocated_Qty", color="SKU",
        barmode="group", title="Allocated Units by Vendor", height=400
    )
    fig_a.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_a, use_container_width=True)
    with st.expander("Show allocation data", expanded=True):
        st.dataframe(df_alloc.style.format({"Allocated_Qty": "{:,}", "MOQ": "{:,}"}), use_container_width=True)
        csv_alloc = df_alloc.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Allocation Data", csv_alloc, "filtered_allocations.csv", "text/csv")

# ----- Fabric Usage Tab -----
with tabs[2]:
    st.markdown("## Fabric Usage Summary")
    fig_fab = px.bar(
        df_fab, x="Fabric_Type", y="Total_Fabric_Required", color="Vendor",
        barmode="group", title="Total Fabric Required by Vendor & Type", height=400
    )
    fig_fab.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_fab, use_container_width=True)
    with st.expander("Show fabric usage data", expanded=True):
        st.dataframe(df_fab.style.format({"Total_Units": "{:,}", "Total_Fabric_Required": "{:,.2f}"}), use_container_width=True)
        csv_fab = df_fab.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Fabric Data", csv_fab, "filtered_fabric_summary.csv", "text/csv")

# ----- Recommendations Tab -----
with tabs[3]:
    st.markdown("## Easy Tips to Save Fabric and Cut Waste")
    st.markdown(
        """
- Track how much fabric you order vs. how much you actually cut to spot waste early.
- Group jobs using the same fabric together to cut fewer rolls and minimize scraps.
- Keep leftover strips and use them for small orders or samples first.
- Lay out your patterns efficiently on the fabric to use up edges and corners.
- If a supplier consistently wastes fabric, reduce small orders for them until their yield improves.
- Share your upcoming orders with vendors so they can buy just the right amount of fabric.
"""
    )




