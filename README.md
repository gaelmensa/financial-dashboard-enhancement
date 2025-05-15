# Financial Stock Dashboard Enhancement (Iteration 1b)

This project is an enhancement of a basic financial stock dashboard, completed as part of a Data Visualization course. The primary goal of this iteration was to implement features for a quick assessment of a stock's historical performance and risk profile, guided by cognitive principles for effective dashboard design and data visualization best practices.

## Deployed Application

The live, interactive dashboard can be accessed here:
**[View Deployed Dashboard](https://financial-dashboard-enhancement-b2sxillc9hd7rnxzh6ulqj.streamlit.app)**

## Key Features Implemented in Iteration 1b

*   **Interactive Stock Price Chart:** Displays historical closing prices for a user-selected stock ticker and date range, with a range slider for intuitive navigation.
*   **Key Statistics Display:** Presents crucial performance and risk metrics in an easily scannable card format:
    *   Total Return (for the selected period)
    *   Annualized Volatility
    *   Number of Trading Days in the period
    *   Average Daily Volume
*   **Historical Data Table:** Provides a detailed view of daily stock data including:
    *   Date, Open, High, Low, Close, Volume
    *   Calculated Daily Return (%)
    *   Conditional color formatting for daily returns (green for positive, red for negative) to aid quick visual analysis.
    *   Sorted by most recent date first.

## Technologies Used

*   **Python:** Core programming language.
*   **Streamlit:** For building and deploying the interactive web application.
*   **Pandas:** For data manipulation and analysis (e.g., calculating returns, preparing tables).
*   **YFinance:** For fetching historical stock market data.
*   **Plotly Express:** For generating the interactive stock price chart.

## Setup and Running Locally

To run this dashboard locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gaelmensa/financial-dashboard-enhancement.git
    cd financial-dashboard-enhancement
    ```

2.  **Create and activate a virtual environment:**
    (Recommended to avoid conflicts with other Python projects)
    ```bash
    python -m venv venv
    ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```

3.  **Install dependencies:**
    Make sure you are in the project directory (`financial-dashboard-enhancement`) where `requirements.txt` is located.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit application:**
    ```bash
    streamlit run financial_dashboard.py
    ```
    The application should open in your default web browser.

## Guiding Principles

The design and implementation of these enhancements were informed by:
*   **Cognitive Principles for Dashboard Design:** Focusing on aspects like Cognitive Load Management, Working Memory Optimization, and Information Chunking.
*   **Data Visualization Principles:** Leveraging concepts such as Data-Ink Ratio and Preattentive Processing to improve clarity and user understanding.