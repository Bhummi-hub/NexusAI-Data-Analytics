import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="NexusAI Data Analytics", page_icon="🚀", layout="wide")

st.title("🚀 NexusAI Data Analytics Platform")
st.markdown("Online Retail Dataset Analysis Dashboard")

# Load the processed dataset automatically
processed_file_path = "data/processed/cleaned_online_retail.csv"

if os.path.exists(processed_file_path):
    @st.cache_data
    def load_data():
        return pd.read_csv(processed_file_path)

    df = load_data()
    
    st.success("Cleaned Online Retail dataset successfully loaded!")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    country_list = df['Country'].unique().tolist()
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + country_list)
    
    if selected_country != "All":
        df = df[df['Country'] == selected_country]
    
    # Overview Metrics
    st.subheader("📊 Key Metrics Overview")
    total_sales = df['TotalPrice'].sum()
    total_orders = df['InvoiceNo'].nunique()
    total_customers = df['CustomerID'].nunique()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales ($)", f"${total_sales:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Unique Customers", f"{total_customers:,}")
    
    # Dataset Preview
    st.subheader("📋 Dataset Preview")
    st.markdown(df.head(10).to_html(classes="dataframe"), unsafe_allow_html=True)
    
    # Visualizations
    st.subheader("📈 Visualizations")
    
    # Top 10 Best Selling Products
    top_products = df.groupby('Description')['Quantity'].sum().reset_index().sort_values(by='Quantity', ascending=False).head(10)
    fig_prod = px.bar(top_products, x='Quantity', y='Description', orientation='h', title="Top 10 Best Selling Products", template="plotly_dark")
    fig_prod.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_prod, use_container_width=True)
    
else:
    st.warning("Processed dataset nahi mila. Pehle `python src/cleaning/preprocess.py` run karein!")

    # Advanced Analytics: RFM Segmentation Preview
    st.subheader("🎯 Customer Segmentation (RFM Analysis)")
    
    # Simple RFM calculation
    # Reference date for Recency
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'count',
        'TotalPrice': 'sum'
    }).rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalPrice': 'Monetary'
    })
    
    # Display top 5 high-value customers
    st.write("Top 5 High-Value Customers (Monetary-wise):")
    st.dataframe(rfm.sort_values(by='Monetary', ascending=False).head(5))