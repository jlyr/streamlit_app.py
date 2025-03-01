import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Set up the main title
st.title("LOL Dataset Visualizations")
st.write("This app demonstrates visualizations based on the LOL dataset.")

# Load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Data PM - case (1).csv")
        return df
    except FileNotFoundError:
        st.error("CSV file not found.")
        return None

# Parse JSON column
def parse_json_column(value):
    try:
        json_data = json.loads(value)
        return json_data.get("total_balance")
    except (json.JSONDecodeError, AttributeError):
        return None

# Load Data
df = load_data()
if df is not None:
    # Preview Data
    st.subheader("Data Preview")
    st.dataframe(df.head())

    # JSON Parsing
    df['total_balance'] = df['POST_TRANSACTION_ACCOUNT_BALANCES'].apply(parse_json_column)

    # Descriptive Statistics
    st.subheader("Descriptive Statistics")
    st.write(df.describe())

    # Seaborn Histogram
    st.subheader("Histogram of Total Balance")
    fig, ax = plt.subplots()
    sns.histplot(df['total_balance'].dropna(), bins=30, kde=True, ax=ax)
    ax.set_title("Distribution of Total Balance")
    st.pyplot(fig)

    # Categorical Bar Plot
    st.subheader("Currency Code Frequency")
    fig2, ax2 = plt.subplots()
    sns.countplot(x='CURRENCY_CODE', data=df, ax=ax2)
    ax2.set_title("Frequency of CURRENCY_CODE")
    st.pyplot(fig2)

    # Line Chart
    st.subheader("Cumulative Balance Trend")
    df['cumsum_balance'] = df['total_balance'].cumsum()
    st.line_chart(df[['cumsum_balance']])

else:
    st.warning("No data to display. Make sure the CSV file is in the directory.")
