import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib.ticker as ticker
sns.set(style='dark')

all_df = pd.read_csv("main_data.csv")
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"]).dt.normalize()

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo 
    st.image("logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

st.header('E-Commerce Analysis Dashboard :sparkles:')


st.subheader('Overview')

overview_df = main_df.groupby("order_purchase_timestamp").agg({"order_id":["nunique"], "price":["sum"]})
overview_df = overview_df.droplevel(0, axis=1)
overview_df.columns = ["count_order", "total_revenue"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_orders_per_day = int(round(overview_df["count_order"].mean()))
    st.metric("Rerata Pesanan / Hari", value=avg_orders_per_day)
with col2:
    median_orders_per_day = int(round(overview_df["count_order"].median()))
    st.metric("Median Pesanan / Hari", value=median_orders_per_day)
with col3:
    max_orders_per_day = int(round(overview_df["count_order"].max()))
    st.metric("Pesanan Tertinggi / Hari", value=max_orders_per_day)
with col4:
    min_orders_per_day = int(round(overview_df["count_order"].min()))
    st.metric("Pesanan Terendah / Hari", value=min_orders_per_day)
fig, ax = plt.subplots(figsize=(20, 10))
plt.plot(overview_df["count_order"])
ax.set_title("Jumlah Pesanan per Hari", loc="center", fontsize=50, pad=24)
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=30)
st.pyplot(fig)

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_total_revenue_per_day = int(round(overview_df["total_revenue"].mean()))
    st.metric("Rerata Pendapatan / Hari", value="$ {:,.0f}".format(avg_total_revenue_per_day))
with col2:
    median_total_revenue_per_day = int(round(overview_df["total_revenue"].median()))
    st.metric("Median Pendapatan / Hari", value="$ {:,.0f}".format(median_total_revenue_per_day))
with col3:
    max_total_revenue_per_day = int(round(overview_df["total_revenue"].max()))
    st.metric("Pendapatan Tertinggi / Hari", value="$ {:,.0f}".format(max_total_revenue_per_day))
with col4:
    min_total_revenue_per_day = int(round(overview_df["total_revenue"].min()))
    st.metric("Pendapatan Terendah / Hari", value="$ {:,.0f}".format(min_total_revenue_per_day))
fig, ax = plt.subplots(figsize=(20, 10))
plt.plot(overview_df["total_revenue"])
ax.set_title("Jumlah Pendapatan per Hari", loc="center", fontsize=50, pad=24)
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=30)
scale_y = 1e3
ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_y))
ax.yaxis.set_major_formatter(ticks_y)
ax.set_ylabel('Ribu', fontsize=30)
st.pyplot(fig)

top_category_table_raw = pd.DataFrame(main_df.groupby(
                        by="product_category_name_english", as_index=False).order_id.count()).sort_values(
                        "order_id", ascending=False).reset_index(drop=True)
top_category_table_raw.rename(columns={
    "product_category_name_english": "product_category",
    "order_id": "order_count"
}, inplace=True)
top_category_table = top_category_table_raw.copy()
top_category_table["product_category"] = top_category_table["product_category"].str.replace("_", " ").str.title()

fig, ax = plt.subplots(figsize=(20, 10))
plt.figure(figsize=(10, 5))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="order_count",
    y="product_category",
    data=top_category_table.head(),
    palette=colors_,
    ax=ax
)
ax.set_title("Kategori Produk Terlaris", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=25)
st.pyplot(fig)

top5_product_category = list(top_category_table_raw["product_category"][:5])
df_top5_product_category = main_df[main_df["product_category_name_english"].isin(top5_product_category)]


st.subheader("Persebaran Lokasi pada 5 Kategori Produk Terlaris")

df_category_state_count = pd.DataFrame(
    df_top5_product_category.groupby(
        "customer_state", as_index=False).order_id.count()).sort_values("order_id").reset_index(drop=True)
df_category_state_count.rename(columns={
    "customer_state": "Customer State",
    "order_id": "Order Count"
}, inplace=True)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors_ = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]
sns.barplot(
    y="Order Count",
    x="Customer State",
    data=df_category_state_count.tail(),
    palette=colors_,
    ax=ax[0]
)
ax[0].set_title("Jumlah Pesanan Tertinggi", loc="center", fontsize=50)
ax[0].set_ylabel(None)
ax[0].set_xlabel("State", fontsize=40)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].invert_xaxis()

colors_ = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]
sns.barplot(
    y="Order Count",
    x="Customer State",
    data=df_category_state_count.head(),
    palette=colors_,
    ax=ax[1]
)
ax[1].set_title("Jumlah Pesanan Terendah", loc="center", fontsize=50)
ax[1].set_ylabel(None)
ax[1].set_xlabel("State", fontsize=40)
ax[1].tick_params(axis='y', labelsize=0)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].invert_xaxis()
ax[1].set_ylim(0,df_category_state_count["Order Count"].max())

st.pyplot(fig)


st.subheader("Pelanggan Terbaik (Analisis RFM & CLTV)")

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "price": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

rfm_df = create_rfm_df(main_df)
rfm_df["first_8_digits"] = rfm_df["customer_unique_id"].str[:8]

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Rerata Recency (hari)", value=avg_recency)
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Rerata Frequency", value=avg_frequency)
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "$ ", locale='es_CO') 
    st.metric("Rerata Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="first_8_digits", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("Recency (hari)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=25)
 
sns.barplot(y="frequency", x="first_8_digits", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=25)
 
sns.barplot(y="monetary", x="first_8_digits", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=25)
 
st.pyplot(fig)

cltv_df = main_df.groupby("customer_unique_id").agg({"order_id": "nunique",
                                                      "order_item_id": "nunique",
                                                      "price": "sum"})
cltv_df.columns = ["total_transaksi", "total_unit", "total_price"]
cltv_df["average_order_value"] = cltv_df["total_price"] / cltv_df["total_transaksi"]
cltv_df["purchase_frequency"] = cltv_df["total_transaksi"] / cltv_df.shape[0]
cltv_df["CV"] = cltv_df["average_order_value"] * cltv_df["purchase_frequency"]
repeat_rate = cltv_df[cltv_df["total_transaksi"] > 1].shape[0] / cltv_df.shape[0]
churn_rate = 1 - repeat_rate
cltv_df["Profit_Margin"] = cltv_df["total_price"] * 0.10
cltv_df["CLTV"] = (cltv_df["CV"] / churn_rate) * cltv_df["Profit_Margin"]
cltv_df["segments"] = pd.qcut(cltv_df["CLTV"], 3, labels= ["LCV", "MCV", "HCV"])
cltv_df.reset_index()
cltv_pivot = cltv_df.groupby("segments").agg({"total_price" : ["count", "mean", "sum"]})
cltv_pivot = cltv_pivot.droplevel(0, axis=1)
cltv_pivot.rename(columns = {"count":"customer_count", "mean":"average_revenue", "sum":"total_revenue"}, inplace=True)
cltv_pivot["average_revenue"] = round(cltv_pivot["average_revenue"]).astype('int')
cltv_pivot["total_revenue"] = round(cltv_pivot["total_revenue"]).astype('int')
cltv_pivot.reset_index(inplace=True)

fig, ax = plt.subplots(figsize=(20, 10))
palette_color = ["#F29789", "#FFD487", "#47B39C"]
ax.pie(x=cltv_pivot["customer_count"], labels=cltv_pivot["segments"], colors=palette_color, autopct='%.0f%%') 
ax.set_title("Proportion of Customer by CLTV Segment", loc="center", fontsize=30, pad=24)
ax.axis('equal')
ax.tick_params(labelsize=30)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(15, 10))
colors_ = ["#F29789", "#FFD487", "#47B39C"]
sns.barplot(
    y="total_revenue",
    x="segments",
    data=cltv_pivot,
    palette=colors_
)
ax.set_title("Total Revenue per CLTV Segment", loc="center", fontsize=30, pad=24)
scale_y = 1e6
ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x/scale_y))
ax.yaxis.set_major_formatter(ticks_y)
ax.set_ylabel('Juta', fontsize=20)
ax.set_xlabel(None)
ax.tick_params(axis='both', labelsize=15)
st.pyplot(fig)