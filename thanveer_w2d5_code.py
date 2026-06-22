import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
df = pd.read_csv(r"cleaned_superstore_data.csv")
    


df["order_date"] = pd.to_datetime(df["order_date"])

# Sidebar Filters
with st.sidebar:
    st.header("Filters")
    with st.form("filters"):
        regions = st.multiselect(
            "Region",
            options=df["region"].unique(),
            default=df["region"].unique(),
        )

        order_year = df["order_date"].dt.year

        years = st.multiselect(
            "Year",
            options=sorted(order_year.unique()),
            default=sorted(order_year.unique()),
        )

        shipping_mode = st.multiselect(
            "Shipping mode",
            options=df["ship_mode"].unique(),
            default=df["ship_mode"].unique(),
        )

        segment = st.multiselect(
            "Segment",
            options=df["segment"].unique(),
            default=df["segment"].unique(),
        )

        submit_button = st.form_submit_button(label="Apply Filters", type="primary")

# Apply Filters
filtered = df[
    (df["region"].isin(regions))
    & (order_year.isin(years))
    & (df["ship_mode"].isin(shipping_mode))
    & (df["segment"].isin(segment))
].copy()    

# Dashboard Title
st.title("📊 Superstore sales_price Dashboard")


# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total sales_price",
        f"${filtered['sales_price'].sum():,.0f}"
    )

with col2:
    st.metric(
        "Total Profit",
        f"${filtered['profit'].sum():,.0f}"
    )

with col3:
    st.metric(
        "Average Discount",
        f"{filtered['discount(%)'].mean():.2%}"
    )

with col4:
    st.metric(
        "order_count",
        f"{filtered['order_id'].nunique()}"
    )

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "By Category", "By Region","Quality Alerts"]
)

# ---------------- TAB 1 ----------------
with tab1:

    
    with st.expander("Shows the row data"):  
         st.dataframe(
         df.head(10),
         use_container_width=True
    )

    # Monthly sales_price by Year
    st.header("Monthly sales_price by Year")

    filtered["order_year"] = filtered["order_date"].dt.year
    filtered["month"] = filtered["order_date"].dt.to_period("M").astype(str)


    monthly_yr = (
        filtered
        .groupby(["month", "order_year"])["sales_price"]
        .sum()
        .reset_index()
    )

    monthly_yr_fig = px.line(
        monthly_yr,
        x="month",
        y="sales_price",
        color="order_year",
        markers=True,
        title="Monthly sales_price Comparison by Year"
    )

    st.plotly_chart(
        monthly_yr_fig,
        use_container_width=True
    )
    st.download_button(
        label="Download Filtered Data",
        data=filtered.to_csv(index=False),
        file_name="filtered_data.csv",
        mime="text/csv",type="primary"
    )
# ---------------- TAB 2 ----------------
with tab2:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Sub-Categories by sales_price")

        top_sub = (
            filtered.groupby("sub_category")["sales_price"]
            .sum()
            .nlargest(10)
            .reset_index()
        )

        fig_bar = px.bar(
            top_sub,
            x="sales_price",
            y="sub_category",
            orientation="h",
            title="Top 10 Sub-Categories"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("sales_price vs Profit by Category")

        scatter_fig = px.scatter(
            filtered,
            x="sales_price",
            y="profit",
            color="category",   # color by category
            hover_data=["sub_category"],
            title="sales_price vs Profit"
        )

        st.plotly_chart(scatter_fig, use_container_width=True)

# ---------------- TAB 3 ----------------
with tab3:

    st.header("Profit Distribution by Region")

    region_profit = (
        filtered.groupby("region")["profit"]
        .sum()
        .reset_index()
    )

    pie_region = px.pie(
        region_profit,
        names="region",
        values="profit",
        hole=0.5,  # Donut chart
        title="Profit Distribution by Region"
    )

    pie_region.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        pie_region,
        use_container_width=True
    )

    st.dataframe(
        region_profit,
        use_container_width=True
    )

    # ---------------- TAB 4 ----------------
with tab4:

    st.header("Quality Alerts")

    #Profit Margin Alert
    profit_margin = np.mean(
        (filtered["profit"] / filtered["sales_price"]) * 100
    )

    if profit_margin > 20:
        st.success(
            f"🟢 Healthy profit margin: {profit_margin:.1f}%"
        )

    elif profit_margin >= 10:
        st.warning(
            f"🟡 Moderate profit margin: {profit_margin:.1f}%"
       )

    else:
        st.error(
            f"🔴 Low profit margin: {profit_margin:.1f}%"
        )

    # 75th Percentile Discount Alert
    p75 = filtered["discount(%)"].quantile(0.75)

    high_discount_orders = (
        filtered["discount(%)"] > p75
    ).sum()

    st.info(
        f"ℹ️ {high_discount_orders} orders above the 75th percentile discount"
    )

    # sales_price Outlier Alert using Z-Score
    z_score = (
        (filtered["sales_price"] - filtered["sales_price"].mean())
        / filtered["sales_price"].std()
    )

    outliers = filtered[abs(z_score) > 2]

    st.warning(
        f"⚠️ {len(outliers)} sales_price outliers detected (|z| > 2)"
    )


    with st.expander("View Outlier Rows"):

         st.dataframe(
         outliers[
            [
                "order_id",
                "order_date",
                "sales_price",
                "profit",
                "region"
            ]
        ],
        use_container_width=True
    )