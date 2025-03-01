import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import csv

st.title("Key Visualizations for Choco PM Case Dataset")

# ----------------------------
# 1) Load the Data
# ----------------------------
def load_data():
    try:
        df = pd.read_csv(
            "Data PM - case (1).csv",
            on_bad_lines='skip',     # Skips badly formatted rows
            engine='python',
            quoting=csv.QUOTE_MINIMAL
        )
        return df
    except FileNotFoundError:
        st.error("CSV file not found.")
        return None
    except pd.errors.ParserError as e:
        st.error(f"ParserError: {e}")
        return None

# Parse JSON columns
def parse_json_column(value):
    try:
        json_data = json.loads(value)
        return json_data.get("total_balance")
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None

# Parse the unnamed_7 column for card_acceptor
def parse_unnamed_7(value):
    try:
        json_data = json.loads(value)
        return json_data.get("card_acceptor", "Unknown")
    except (json.JSONDecodeError, TypeError, AttributeError):
        return "Unknown"

df = load_data()

if df is not None:
    # Extract total_balance from POST_TRANSACTION_ACCOUNT_BALANCES
    if 'POST_TRANSACTION_ACCOUNT_BALANCES' in df.columns:
        df['total_balance'] = df['POST_TRANSACTION_ACCOUNT_BALANCES'].apply(parse_json_column)
    
    # Extract card_acceptor from Unnamed: 7 column if it exists
    if 'Unnamed: 7' in df.columns:
        df['card_acceptor'] = df['Unnamed: 7'].apply(parse_unnamed_7)
        # Print value counts for debugging
        print(f"MCC column exists: {'MCC' in df.columns}")
        print("Card acceptor values:", df['card_acceptor'].value_counts().head())

    # Display a quick preview
    st.subheader("Data Preview")
    st.dataframe(df.head())

    # Ensure columns exist before plotting
    # needed_cols = ['AMOUNT', 'BOOKING_DATE', 'MCC', 'CURRENCY_CODE', 'total_balance']
    # for col in needed_cols:
    #     if col not in df.columns:
    #         st.warning(f"Column '{col}' is missing from your CSV. Visualizations may fail.")
    st.write("---")

    # ----------------------------
    # 1) Distribution of Transaction Amounts
    # ----------------------------
    st.subheader("1. Distribution of Transaction Amounts")
    if 'AMOUNT' in df.columns:
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.histplot(df['AMOUNT'], bins=50, ax=ax1)
        ax1.set_title('Distribution of Transaction Amounts')
        ax1.set_xlabel('Transaction Amount (SGD)')
        ax1.set_ylabel('Frequency')
        st.pyplot(fig1)

        st.markdown(
            "**Insight:** This shows how transaction amounts are distributed. "
            "We can see whether most transactions cluster around certain values, "
            "and also identify outliers (e.g., large debits or credits)."
        )
    else:
        st.warning("Column 'AMOUNT' not found. Cannot display Distribution of Transaction Amounts.")

    st.write("---")

    # ----------------------------
    # 2) Box Plot of Transaction Amounts by Currency
    # ----------------------------
    st.subheader("2. Box Plot of Transaction Amounts by Currency")
    if {'CURRENCY_CODE', 'AMOUNT'}.issubset(df.columns):
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.boxplot(x='CURRENCY_CODE', y='AMOUNT', data=df, ax=ax2)
        ax2.set_title('Transaction Amounts by Currency')
        ax2.set_xlabel('Currency')
        ax2.set_ylabel('Transaction Amount (SGD)')
        st.pyplot(fig2)

        st.markdown(
            "**Insight:** The box plot helps compare distributions of transaction amounts "
            "across different currencies. It highlights the median, quartiles, and outliers."
        )
    else:
        st.warning("Columns 'CURRENCY_CODE' and/or 'AMOUNT' not found. Cannot display Box Plot.")

    st.write("---")

    
    # ----------------------------
    # 3) Scatter Plot of Transaction Amount vs. Total Balance
    # ----------------------------
    st.subheader("3. Scatter Plot: Transaction Amount vs. Total Balance")
    if {'AMOUNT', 'total_balance'}.issubset(df.columns):
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x='AMOUNT', y='total_balance', data=df, ax=ax4)
        ax4.set_title('Transaction Amount vs. Total Balance')
        ax4.set_xlabel('Transaction Amount (SGD)')
        ax4.set_ylabel('Total Balance (SGD)')
        st.pyplot(fig4)

        st.markdown(
            "**Insight:** This visualization helps identify potential correlations or patterns "
            "between transaction amounts and account balances. Larger debits might lead to lower balances, etc."
        )
    else:
        st.warning("Columns 'AMOUNT' and/or 'total_balance' not found. Cannot display Scatter Plot.")

    st.write("---")

    # ----------------------------
    # 3) Time Series of Transaction Amounts (If Timestamp Data Available)
    # ----------------------------
    st.subheader("4. Time Series of Transaction Amounts")
    if {'AMOUNT', 'BOOKING_DATE'}.issubset(df.columns):
        try:
            # Convert 'BOOKING_DATE' to datetime and set it as index
            df['BOOKING_DATE'] = pd.to_datetime(df['BOOKING_DATE'])
            df_time = df.copy()  # Create a copy to avoid affecting other visualizations
            df_time.set_index('BOOKING_DATE', inplace=True)
            
            # Create a daily sum timeseries
            fig5, ax5 = plt.subplots(figsize=(12, 6))
            df_time['AMOUNT'].resample('D').sum().plot(ax=ax5)
            ax5.set_title('Daily Sum of Transaction Amounts')
            ax5.set_xlabel('Date')
            ax5.set_ylabel('Total Transaction Amount (SGD)')
            st.pyplot(fig5)

            st.markdown(
                "**Insight:** This shows the daily trend of transaction amounts over time, "
                "revealing potential daily, weekly, or seasonal patterns."
            )
        except Exception as e:
            st.error(f"Error in Time Series plotting: {e}")
    else:
        st.warning("Columns 'AMOUNT' and/or 'BOOKING_DATE' not found. Cannot display Time Series.")

    # ----------------------------
    # 5) Analyze the impact of negative values in 'AMOUNT'
    # ----------------------------
    st.subheader("5. Impact of Negative Values in AMOUNT")
    if 'AMOUNT' in df.columns:
        # Get stats for negative amounts
        negative_amount_stats = df[df['AMOUNT'] < 0]['AMOUNT'].describe()
        overall_amount_stats = df['AMOUNT'].describe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Negative Amount Statistics")
            st.dataframe(pd.DataFrame(negative_amount_stats))
            
        with col2:
            st.markdown("### Overall Amount Statistics")
            st.dataframe(pd.DataFrame(overall_amount_stats))
        
        # Plot distribution of negative vs positive amounts
        fig6, ax6 = plt.subplots(figsize=(10, 6))
        df['Amount_Type'] = df['AMOUNT'].apply(lambda x: 'Debit (Negative)' if x < 0 else 'Credit (Positive)')
        sns.boxplot(x='Amount_Type', y='AMOUNT', data=df, ax=ax6)
        ax6.set_title('Distribution of Transaction Amounts by Type')
        ax6.set_xlabel('Transaction Type')
        ax6.set_ylabel('Amount (SGD)')
        st.pyplot(fig6)
        
        st.markdown(
            "**Insight:** Analyzing negative values separately helps understand spending patterns "
            "versus income/deposits. Negative values typically represent payments, purchases, or withdrawals."
        )
    else:
        st.warning("Column 'AMOUNT' not found. Cannot analyze impact of negative values.")

else:
    st.error("No data loaded. Please ensure the CSV file is in the directory and named correctly.")
