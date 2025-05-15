from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# Set page config - THIS SHOULD BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Stock Market Dashboard - Metrics", layout="wide")

# Add title and description
st.title("Stock Market Dashboard")
st.subheader("Iteration 1b: Key Statistics and Metrics") # You can keep this or adjust later

# Stock selector and date range from iteration 1a
ticker_symbol = st.text_input("Enter Stock Ticker Symbol", "AAPL").upper().strip()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", date.today() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", date.today())

# Input validation
if start_date > end_date:
    st.error("Start date must be before end date") # Changed from st.write to st.error
    st.stop()

if start_date > date.today():
    st.error("Start date must be before today") # Changed from st.write to st.error
    st.stop()

if end_date > date.today():
    st.error("End date must be before today") # Changed from st.write to st.error
    st.stop()


# Fetch data using yfinance (from iteration 1a)
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_stock_data(ticker, start, end):
    print(f"Attempting to fetch data for: {ticker} from {start} to {end}")
    try:
        # yf.download for a single ticker can return columns as MultiIndex
        # e.g., columns=[('Close', 'AAPL'), ('Volume', 'AAPL')]
        stock_data_raw = yf.download(ticker, start=start, end=end, progress=False)
        
        print(f"yf.download for {ticker} returned object of type: {type(stock_data_raw)}")
        if isinstance(stock_data_raw, pd.DataFrame):
            print(f"It's a DataFrame with shape: {stock_data_raw.shape}")
            print("Columns:", stock_data_raw.columns)
            print("Head:\n", stock_data_raw.head())

        if stock_data_raw.empty:
            st.warning(f"No data found for {ticker} between {start} and {end}. Try a different ticker or date range.")
            print(f"Data for {ticker} is empty.")
            return None, None

        # Correctly access 'Close' data if columns are MultiIndex
        # The first level name is often 'Price' or just the metric name if not explicitly grouped by yfinance
        # The second level name is the ticker
        # We need to find the exact column name for 'Close'.
        # A robust way is to select by level if MultiIndex, or direct if simple index.
        
        # Try to get the 'Close' column specifically for the given ticker
        # yfinance might sometimes return just 'Close' or ('Close', ticker_symbol)
        # or even just the ticker_symbol as the second level of MultiIndex
        if isinstance(stock_data_raw.columns, pd.MultiIndex):
            # Try common MultiIndex patterns for a single ticker
            if ('Close', ticker) in stock_data_raw.columns:
                close_prices = stock_data_raw[('Close', ticker)]
            elif 'Close' in stock_data_raw.columns.get_level_values(0): # if 'Close' is a top-level name
                 # This might select a DataFrame if multiple tickers were under 'Close',
                 # but for a single ticker download, it should be specific enough if 'ticker' is the 2nd level
                if ticker in stock_data_raw['Close'].columns: # Check if ticker is a sub-column of 'Close'
                    close_prices = stock_data_raw['Close'][ticker]
                else: # If 'Close' itself is a DataFrame with a single column (the ticker's close)
                    close_prices = stock_data_raw['Close'].iloc[:,0]
            else: # Fallback or error if 'Close' can't be clearly identified
                st.error(f"Could not isolate 'Close' prices for {ticker} from MultiIndex columns.")
                print(f"Failed to find 'Close',{ticker} in MultiIndex: {stock_data_raw.columns}")
                return None, None
        elif 'Close' in stock_data_raw.columns: # Simple columns
            close_prices = stock_data_raw['Close']
        else:
            st.error(f"'Close' column not found in data for {ticker}.")
            print(f"'Close' column not found for {ticker} in simple columns: {stock_data_raw.columns}")
            return None, None
            
        if not isinstance(close_prices, pd.Series):
             # This should ideally not be reached if the logic above is correct
            st.error(f"Isolated 'Close' data for {ticker} is not a Series. Type: {type(close_prices)}")
            print(f"Error: 'Close' for {ticker} is not a Series after access. Type: {type(close_prices)}")
            return None, None

        df_for_chart = pd.DataFrame({
            "date": stock_data_raw.index,
            "close": close_prices
        })
        
        print(f"Successfully prepared df_for_chart for {ticker}.")
        # We need to return a modified stock_data_raw that has simple column names
        # for easier use in metric calculations.
        # Let's flatten the MultiIndex columns if present.
        
        if isinstance(stock_data_raw.columns, pd.MultiIndex):
            # Flatten MultiIndex: use the first level (e.g., 'Close', 'Open')
            # This assumes the second level (ticker) is redundant as we only fetch one.
            simple_cols_df = stock_data_raw.copy()
            simple_cols_df.columns = simple_cols_df.columns.get_level_values(0)
            # Check for duplicate column names after flattening (e.g. if 'Price' was also a column name)
            if simple_cols_df.columns.duplicated().any():
                # A more sophisticated de-duplication might be needed for generic cases,
                # but for yfinance OHLCV, get_level_values(0) should be unique.
                print("Warning: Duplicate column names after flattening MultiIndex. Using first occurrence.")
                simple_cols_df = simple_cols_df.loc[:,~simple_cols_df.columns.duplicated()]
            print("Flattened MultiIndex columns for metric calculation.")
            return simple_cols_df, df_for_chart
        else:
            return stock_data_raw, df_for_chart # Already has simple columns
        
    except Exception as e:
        st.error(f"Error in get_stock_data for {ticker}: {e}")
        import traceback
        print(f"--- TRACEBACK for {ticker} ---")
        traceback.print_exc()
        print(f"--- END TRACEBACK for {ticker} ---")
        return None, None
    
    
    


# Display loading message
with st.spinner(f"Loading data for {ticker_symbol}..."):
    # 'stock_data' here will be the raw yfinance data, 'df' is for the chart
    stock_data, df_chart = get_stock_data(ticker_symbol, start_date, end_date)

# Check if data was fetched successfully
if stock_data is not None and not stock_data.empty and df_chart is not None and not df_chart.empty:
    # Display the stock price chart (from iteration 1a)
    st.subheader(f"{ticker_symbol} Stock Price")

    fig = px.line(
        df_chart, # Use df_chart here
        x="date",
        y="close",
        title=f"{ticker_symbol} Closing Price",
        labels={"close": "Price (USD)", "date": "Date"},
        template="plotly_white",
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        legend_title_text="",
        height=500,
    )
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- Iteration 1b: Key Statistics and Metrics ---
    # THIS IS WHERE THE NEW CODE BLOCK BEGINS
    # (The one from my previous message that starts with st.subheader("Key Statistics"))

    st.subheader("Key Statistics")

    # 1. Calculate Metrics
    # Ensure stock_data index is DatetimeIndex for pct_change
    if not isinstance(stock_data.index, pd.DatetimeIndex):
        stock_data.index = pd.to_datetime(stock_data.index)

    stock_data_copy = stock_data.copy() # Use the raw stock_data here
    #print("DEBUG: Type of stock_data_copy['Close'] BEFORE pct_change:", type(stock_data_copy['Close'])) # DEBUG
    #print("DEBUG: stock_data_copy['Close'].head() BEFORE pct_change:\n", stock_data_copy['Close'].head()) # DEBUG
    stock_data_copy['Daily Return'] = stock_data_copy['Close'].pct_change()

    if len(stock_data_copy['Close']) > 1:
        total_return = (stock_data_copy['Close'].iloc[-1] / stock_data_copy['Close'].iloc[0]) - 1
        annualized_volatility = stock_data_copy['Daily Return'].std() * (252**0.5)
    else:
        total_return = 0.0
        annualized_volatility = float('nan') # Explicitly NaN

    num_trading_days = len(stock_data_copy)
    avg_daily_volume = stock_data_copy['Volume'].mean()

    # 2. Create Metrics Dashboard
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    with col_metric1:
        st.metric(label="Total Return (Period)", value=f"{total_return:.2%}")
    with col_metric2:
        st.metric(label="Annualized Volatility", value=f"{annualized_volatility:.2%}" if pd.notna(annualized_volatility) else "N/A")
    with col_metric3:
        st.metric(label="Trading Days", value=f"{num_trading_days}")
    with col_metric4:
        st.metric(label="Avg. Daily Volume", value=f"{avg_daily_volume:,.0f}" if pd.notna(avg_daily_volume) else "N/A")

    st.markdown("---")

    # 3. Create and Display Data Table
    st.subheader("Historical Data with Daily Returns")
    table_data = stock_data_copy[['Open', 'High', 'Low', 'Close', 'Volume', 'Daily Return']].copy()
    table_data.index.name = 'Date'
    table_data.reset_index(inplace=True)
    table_data['Date'] = table_data['Date'].dt.strftime('%Y-%m-%d')
    table_data.sort_values(by='Date', ascending=False, inplace=True)

    def style_negative_red(val):
        if isinstance(val, (int, float)) and pd.notna(val):
            color = 'red' if val < 0 else ('green' if val > 0 else 'black')
            return f'color: {color}'
        return ''

    st.dataframe(
        table_data.style.format({
            'Daily Return': "{:.2%}", 'Open': "{:.2f}", 'High': "{:.2f}",
            'Low': "{:.2f}", 'Close': "{:.2f}", 'Volume': "{:,.0f}"
        }).map(style_negative_red, subset=['Daily Return']),
        hide_index=True,
        use_container_width=True
    )
    # --- End of Iteration 1b Code ---

else: # This 'else' corresponds to the 'if stock_data is not None ...'
    # This part only runs if stock_data or df_chart is None or empty from the start
    if not (stock_data is not None and not stock_data.empty and df_chart is not None and not df_chart.empty):
         # The original error message about checking ticker and trying again
        st.error(
             f"No data found for {ticker_symbol}. Please check the ticker symbol and try again."
        )
        st.info("Try using a valid ticker like AAPL, MSFT, GOOGL, or AMZN.")