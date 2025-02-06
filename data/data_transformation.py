import os
import pandas as pd
import numpy as np
import streamlit as st
import chardet
import pdfplumber
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore

# 📌 Function to detect file encoding
def detect_encoding(file):
    raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

# 📌 Function to load the file and detect encoding
def load_dataset(uploaded_file):
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension == "csv":
            file_encoding = detect_encoding(uploaded_file)
            uploaded_file.seek(0)  
            df = pd.read_csv(uploaded_file, encoding=file_encoding, sep=None, engine="python")

        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file)

        elif file_extension == "json":
            df = pd.read_json(uploaded_file)

        elif file_extension == "pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
                df = pd.DataFrame([line.split() for line in text.split("\n") if line])
        elif file_extension == "pdf":
             df = pdf_to_dataframe(uploaded_file)

        else:
            st.error("❌ Unsupported format. Please upload a CSV, Excel, JSON, or PDF file.")
            return None

        return df

    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        return None


def pdf_to_dataframe(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        tables = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.append(pd.DataFrame(table[1:], columns=table[0]))
        return pd.concat(tables, ignore_index=True) if tables else None

# 📌 Function to display a detailed summary of the dataset
def summarize_data(df):
    st.subheader("📊 Dataset Summary")

    col1, col2 = st.columns(2)  

    with col1:
        st.write("### 📋 General Statistics")
        summary_df = pd.DataFrame({
            "Statistic": ["Number of Rows", "Number of Columns", "Missing Values", "Duplicates"],
            "Value": [df.shape[0], df.shape[1], df.isnull().sum().sum(), df.duplicated().sum()]
        })
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

    with col2:
        st.write("### 📑 Data Types")
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str)
        })
        st.dataframe(dtype_df, hide_index=True, use_container_width=True)

    st.write("### 🔍 Preview of First Rows")
    st.dataframe(df.head())

# 📌 Function to handle missing values
def handle_missing_values(df, strategy="mean"):
    if df.isnull().sum().sum() == 0:
        return df

    st.write(f"🛠 **Handling missing values:** `{strategy}`")
    if strategy == "mean":
        df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
        df.fillna(df.select_dtypes(exclude=["number"]).mode().iloc[0], inplace=True)
    elif strategy == "median":
        df.fillna(df.select_dtypes(include=["number"]).median(), inplace=True)
        df.fillna(df.select_dtypes(exclude=["number"]).mode().iloc[0], inplace=True)
    elif strategy == "most frequent value":
        df.fillna(df.mode().iloc[0], inplace=True)
    elif strategy == "drop":
        df.dropna(inplace=True)

    st.write("### 🔍 Preview after handling missing values")
    st.dataframe(df.head())
    return df

# 📌 Function to remove duplicates
def handle_duplicates(df, handle_dupes="Remove"):
    before = df.shape[0]

    if handle_dupes == "Remove":
        df = df.drop_duplicates()
        after = df.shape[0]
        st.write(f"🔄 **Duplicates removed:** {before - after} rows deleted")
    else:
        st.write("✅ **No duplicate removal.** Data remains unchanged.")

    st.write("### 🔍 Preview of data after handling duplicates")
    st.dataframe(df.head())

    return df

# 📌 Function to handle outliers with chosen strategy
def handle_outliers(df, strategy="nothing", threshold=3):
    numeric_cols = df.select_dtypes(include=[np.number])
    if len(numeric_cols.columns) == 0:
        return df

    # Calculate Z-scores to identify outliers
    z_scores = np.abs(zscore(numeric_cols))
    outliers = (z_scores > threshold)

    if strategy == "nothing":
        st.write("🛠 **No transformation applied to outliers.**")
    else:
        if strategy == "log_transformation":
            st.write("🛠 **Applying logarithmic transformation to outliers.**")
            for col in numeric_cols.columns:
                df[col] = df[col].apply(lambda x: np.log(x + 1) if x > 0 else x)

        elif strategy == "mean":
            st.write("🛠 **Replacing outliers with mean.**")
            for col in numeric_cols.columns:
                mean_val = df[col].mean()
                df.loc[outliers[col], col] = mean_val

        elif strategy == "median":
            st.write("🛠 **Replacing outliers with median.**")
            for col in numeric_cols.columns:
                median_val = df[col].median()
                df.loc[outliers[col], col] = median_val

        elif strategy == "drop":
            st.write(f"🛠 **Removing rows with outliers.**")
            before = df.shape[0]
            df = df[~outliers.any(axis=1)]
            after = df.shape[0]
            st.write(f"🚀 **Outliers removed:** {before - after} rows")

    # 📌 Select a column for visualization
    selected_col = st.selectbox("📊 Select a column to visualize:", numeric_cols.columns)

    # 📊 Visualization before transformation
    st.write(f"### 📊 Distribution of `{selected_col}` before handling outliers")
    fig, ax = plt.subplots(figsize=(8, 4))
    numeric_cols[selected_col].hist(bins=30, edgecolor="black", ax=ax)
    st.pyplot(fig)

    # 📊 Visualization after transformation
    st.write(f"### 📊 Distribution of `{selected_col}` after handling outliers")
    fig, ax = plt.subplots(figsize=(8, 4))
    df[selected_col].hist(bins=30, edgecolor="black", ax=ax)
    st.pyplot(fig)

    st.write("### 🔍 Preview of data after handling outliers")
    st.dataframe(df.head())

    return df