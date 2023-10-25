import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
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


st.subheader('Jumlah Transaksi Barang')

top_category_table_raw = pd.DataFrame(main_df.groupby(
                        by="product_category_name_english", as_index=False).order_id.count()).sort_values(
                        "order_id", ascending=False).reset_index(drop=True)
top_category_table_raw.rename(columns={
    "product_category_name_english": "product_category",
    "order_id": "order_count"
}, inplace=True)
top_category_table = top_category_table_raw.copy()
top_category_table["product_category"] = top_category_table["product_category"].str.replace("_", " ").str.title()

total_orders = top_category_table.order_count.sum()
st.metric("Total Pesanan", value=total_orders)

fig, ax = plt.subplots(figsize=(20, 10))
plt.figure(figsize=(10, 5))
colors_ = ["#008000", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="order_count",
    y="product_category",
    data=top_category_table.head(),
    palette=colors_,
    ax=ax
)
ax.set_title("Largest number of Orders by Product Category", loc="center", fontsize=50)
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

colors_ = ["#008000", "#008000", "#008000", "#008000", "#008000"]
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

colors_ = ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"]
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


st.subheader("Pelanggan Terbaik Berdasarkan Parameter RFM")

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

rfm_df = create_rfm_df(main_df)
rfm_df["first_7_digits"] = rfm_df["customer_id"].str[:7]

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
 
sns.barplot(y="recency", x="first_7_digits", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=25)
 
sns.barplot(y="frequency", x="first_7_digits", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=25)
 
sns.barplot(y="monetary", x="first_7_digits", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=25)
 
st.pyplot(fig)
