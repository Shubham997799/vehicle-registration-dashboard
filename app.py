import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# Load data function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('vehicle_registrations.csv')
        df['date'] = pd.to_datetime(df['date'])
    except:
        # Generate mock data if file doesn't exist
        categories = ['2W', '3W', '4W']
        manufacturers = {
            '2W': ['Hero', 'Honda', 'Bajaj', 'TVS', 'Royal Enfield'],
            '3W': ['Bajaj', 'Mahindra', 'Piaggio', 'TVS'],
            '4W': ['Maruti', 'Hyundai', 'Tata', 'Mahindra', 'Kia', 'Toyota']
        }
        
        dates = pd.date_range(start='2019-01-01', end='2023-12-31', freq='M')
        data = []
        
        for date in dates:
            for category in categories:
                for manufacturer in manufacturers.get(category, []):
                    base = np.random.randint(1000, 5000)
                    growth = (date.year - 2019) * 0.15
                    seasonality = np.sin((date.month - 1) * np.pi / 6) * 0.2
                    noise = np.random.normal(0, 0.1)
                    registrations = int(base * (1 + growth + seasonality + noise))
                    
                    data.append({
                        'date': date,
                        'year': date.year,
                        'quarter': f'Q{(date.month-1)//3 + 1}',
                        'month': date.month,
                        'category': category,
                        'manufacturer': manufacturer,
                        'registrations': max(1000, registrations)
                    })
        
        df = pd.DataFrame(data)
        df.to_csv('vehicle_registrations.csv', index=False)
    return df

# Main app
def main():
    st.set_page_config(layout="wide")
    st.title("🚗 Vehicle Registration Dashboard")
    st.markdown("Investor-focused analysis of vehicle registration trends")
    
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input(
        "Date range",
        [df['date'].min(), df['date'].max()],
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )
    
    categories = st.sidebar.multiselect(
        "Vehicle Categories",
        options=df['category'].unique(),
        default=df['category'].unique()
    )
    
    manufacturers = st.sidebar.multiselect(
        "Manufacturers",
        options=df['manufacturer'].unique(),
        default=df['manufacturer'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['date'] >= pd.to_datetime(date_range[0])) &
        (df['date'] <= pd.to_datetime(date_range[1])) &
        (df['category'].isin(categories)) &
        (df['manufacturer'].isin(manufacturers))
    ]
    
    # Metrics
    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_reg = filtered_df['registrations'].sum()
        st.metric("Total Registrations", f"{total_reg:,}")
    
    with col2:
        yoy_growth = (filtered_df[filtered_df['year'] == 2023]['registrations'].sum() / 
                    filtered_df[filtered_df['year'] == 2022]['registrations'].sum() - 1) * 100
        st.metric("YoY Growth (2023)", f"{yoy_growth:.1f}%")
    
    with col3:
        latest_month = filtered_df['date'].max().strftime('%B %Y')
        st.metric("Latest Data", latest_month)
    
    # Visualizations
    st.header("Trend Analysis")
    
    # YoY Growth
    st.subheader("Year-over-Year Growth")
    yoy_df = filtered_df.groupby('year')['registrations'].sum().reset_index()
    yoy_df['growth_pct'] = yoy_df['registrations'].pct_change() * 100
    fig_yoy = px.bar(yoy_df, x='year', y='growth_pct', 
                    title="YoY Growth Percentage", text_auto='.1f')
    st.plotly_chart(fig_yoy, use_container_width=True)
    
    # Manufacturer Share
    st.subheader("Manufacturer Market Share")
    manu_share = filtered_df.groupby('manufacturer')['registrations'].sum().reset_index()
    fig_share = px.pie(manu_share, values='registrations', names='manufacturer',
                      title="Manufacturer Market Share")
    st.plotly_chart(fig_share, use_container_width=True)
    
    # Time Series
    st.subheader("Monthly Registration Trends")
    monthly = filtered_df.groupby(['date', 'category'])['registrations'].sum().reset_index()
    fig_trend = px.line(monthly, x='date', y='registrations', color='category',
                       title="Monthly Registration Trends by Vehicle Type")
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Raw Data
    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Data")
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
