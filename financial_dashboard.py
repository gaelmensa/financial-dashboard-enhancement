from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# Set page config
st.set_page_config(page_title="Stock Market Dashboard - Metrics", layout="wide")

# Add title and description
st.title("Stock Market Dashboard")
st.subheader("Iteration 1b: Key Statistics and Metrics")

# Stock selector and date range from iteration 1a
ticker_symbol = st.text_input("Enter Stock Ticker Symbol", "AAPL").upper().strip()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", date.today() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", date.today())

# Input validation
if start_date > end_date:
    st.write("Start date must be before end date")
    st.stop()

if start_date > date.today():
    st.write("Start date must be before today")
    st.stop()

if end_date > date.today():
    st.write("End date must be before today")
    st.stop()


# Fetch data using yfinance (from iteration 1a)
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_stock_data(ticker, start, end):
    try:
        # Get the stock data
        stock_data = yf.download(ticker, start=start, end=end)

        if stock_data.empty:
            return None

        # Extract date and close price directly without assuming column structure
        # Just convert the data to a simple format that plotly can handle
        df = pd.DataFrame(
            {
                "date": stock_data.index,
                "close": stock_data["Close"][ticker]
                if isinstance(stock_data["Close"], pd.DataFrame)
                else stock_data["Close"],
            }
        )

        # Also return the original stock data for additional calculations
        return stock_data, df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None


# Display loading message
with st.spinner(f"Loading data for {ticker_symbol}..."):
    stock_data, df = get_stock_data(ticker_symbol, start_date, end_date)

# Check if data was fetched successfully
if stock_data is not None and not stock_data.empty:
    # Display the stock price chart (from iteration 1a)
    st.subheader(f"{ticker_symbol} Stock Price")

    fig = px.line(
        df,
        x="date",
        y="close",
        title=f"{ticker_symbol} Closing Price",
        labels={"close": "Price (USD)", "date": "Date"},
        template="plotly_white",
    )

    # Format the chart with useful titles
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        legend_title_text="",
        height=500,
    )

    # Add minimap to help with confirmation bias (you can see the whole
    # year even if you are zoomed in) and to help with time selection
    fig.update_xaxes(rangeslider_visible=True)

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Your code goes here:
    # 1. Calculate daily returns and other metrics
    # 2. Create metrics dashboard with key statistics
    # 3. Create and display data table with conditional formatting
else:
    st.error(
        f"No data found for {ticker_symbol}. Please check the ticker symbol and try again."
    )
    st.info("Try using a valid ticker like AAPL, MSFT, GOOGL, or AMZN.")