# IMPORT LIBRARY
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# HELPER FUNCTIONS
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df


def create_category_sales_df(df):
    category_df = df.groupby("product_category_name").agg({
        "order_id": "count",
        "price": "sum"
    }).reset_index()

    category_df.rename(columns={
        "order_id": "total_orders",
        "price": "total_revenue"
    }, inplace=True)

    return category_df.sort_values(by="total_orders", ascending=False)


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })

    rfm_df.columns = ["customer_id", "last_order", "frequency", "monetary"]

    rfm_df["last_order"] = rfm_df["last_order"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()

    rfm_df["recency"] = rfm_df["last_order"].apply(
        lambda x: (recent_date - x).days
    )

    rfm_df.drop("last_order", axis=1, inplace=True)

    return rfm_df

# LOAD DATA
all_df = pd.read_csv("main_data.csv")

# convert datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

# sort
all_df.sort_values(by="order_purchase_timestamp", inplace=True)

# FILTER
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://framerusercontent.com/images/ajZOW8b95H9bhENjPzPOTROJ3Qk.png", width=150)

    st.header("Filter Waktu")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date)) &
    (all_df["order_purchase_timestamp"] <= str(end_date))
]

# PREP DATA
daily_orders_df = create_daily_orders_df(main_df)
category_df = create_category_sales_df(main_df)
rfm_df = create_rfm_df(main_df)

# DASHBOARD
st.header("E-Commerce Dashboard 📊")

# METRIC
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df["order_count"].sum()
    st.metric("Total Orders", total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df["revenue"].sum(),
        "BRL",
        locale='pt_BR'
    )
    st.metric("Total Revenue", total_revenue)


# TREND
st.subheader("Tren Pesanan")

fig, ax = plt.subplots(figsize=(12,5))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o'
)

ax.set_title("Jumlah Pesanan per Hari")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Order")

st.pyplot(fig)

# TOP CATEGORY
st.subheader("Top 10 Kategori Produk")

top_category = category_df.head(10)

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(
    x="total_orders",
    y="product_category_name",
    data=top_category,
    ax=ax
)

ax.set_title("Kategori dengan Penjualan Terbanyak")

st.pyplot(fig)

# RFM
st.subheader("RFM Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Avg Recency", round(rfm_df.recency.mean(),1))

with col2:
    st.metric("Avg Frequency", round(rfm_df.frequency.mean(),2))

with col3:
    st.metric("Avg Monetary", round(rfm_df.monetary.mean(),2))


fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20,5))

sns.barplot(
    x="customer_id",
    y="recency",
    data=rfm_df.sort_values(by="recency").head(5),
    ax=ax[0]
)
ax[0].set_title("Best Recency")

sns.barplot(
    x="customer_id",
    y="frequency",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    ax=ax[1]
)
ax[1].set_title("Top Frequency")

sns.barplot(
    x="customer_id",
    y="monetary",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    ax=ax[2]
)
ax[2].set_title("Top Monetary")

st.pyplot(fig)

# FOOTER
st.caption("E-Commerce Dashboard - 2026")