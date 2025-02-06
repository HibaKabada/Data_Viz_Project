import streamlit as st
# Streamlit app configuration
st.set_page_config(page_title="Chatbot App", page_icon="🤖", layout="wide")
from data.data_transformation import (
    load_dataset, 
    summarize_data, 
    handle_missing_values, 
    handle_duplicates, 
    handle_outliers
)

# Initialize session state for storing transformed data
if "transformed_df" not in st.session_state:
    st.session_state.transformed_df = None

with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to", ["How to use", "Chatbot", "Data Transformation", "About"])
    
    if page == "Chatbot":
        None

if page == "How to use":
    None

# Page: Data Transformation
elif page == "Data Transformation":
    st.title("📊 Data Cleaning & Transformation")
    uploaded_file = st.file_uploader("Upload your dataset (CSV, Excel, JSON, PDF)", type=["csv", "xlsx", "json", "pdf"])
    
    if uploaded_file:
        try:
            df = load_dataset(uploaded_file)
            if df is not None:
                summarize_data(df)
                
                # Handling missing values
                st.subheader("💪 Handle Missing Values")
                strategy = st.selectbox("Select strategy", ["mean", "median", "valeur la plus fréquente", "drop"])
                df = handle_missing_values(df, strategy)
                
                # Handling duplicates
                st.subheader("🛠️ Handle Duplicates")
                handle_dupes = st.radio("Choose action", ["Keep", "Supprimer"])
                df = handle_duplicates(df, handle_dupes)
                
                # Handling outliers
                st.subheader("🌟 Handle Outliers")
                outlier_strategy = st.selectbox("Choose strategy", ["nothing", "log_transformation", "mean"])
                df = handle_outliers(df, outlier_strategy)
                
                st.session_state.transformed_df = df
                st.success("Data transformation applied successfully!")
        except Exception as e:
            st.error(f"Error processing file: {e}")

                # 📤 Option pour télécharger le fichier transformé
        st.download_button(
                    label="📥 Télécharger les données transformées",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="data_cleaned.csv",
                    mime="text/csv"
                )   

# Page: Chatbot
elif page == "Chatbot":
    None
# Page: About
elif page == "About":
    None
