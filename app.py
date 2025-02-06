import streamlit as st
# Streamlit app configuration
st.set_page_config(page_title="QueryGenius", page_icon="🤖", layout="wide")
from data.data_transformation import (
    load_dataset, 
    summarize_data, 
    handle_missing_values, 
    handle_duplicates, 
    handle_outliers
)

st.markdown("""
    <style>
        .title-container {
            margin-top: 0px; /* Reducing space above */
            margin-bottom: 5px; /* Optional: Reducing space below */
        }
    </style>
    <div class="title-container">
        <h2 style='text-align: center;'>🚀 Unlock the Power of Data & Chat with</h2>
        <h1 style='text-align: center; font-weight: bold;'>QueryGenius </h1>
    </div>
""", unsafe_allow_html=True)


# Initialize session state for storing transformed data
if "transformed_df" not in st.session_state:
    st.session_state.transformed_df = None

with st.sidebar:
    # Logo and chatbot name
    st.markdown("<h2 style='text-align: center;'>QueryGenius</h2>", unsafe_allow_html=True)
    
    # Sidebar navigation
    page = st.radio("Go to", ["How to use", "Chatbot", "Data Transformation", "About"])
    
    if page == "Chatbot":
        None

if page == "How to use":


    

    
    st.markdown("""
         
        This application allows you to interact with a chatbot and perform data cleaning and transformation.  
        Below is a guide on how to use each section:
    """)

    st.subheader("🤖 Chatbot")
    st.markdown("""
        - Navigate to the **Chatbot** page from the sidebar.
        - Choose the type of API key you possess and upload your dataset.
        - A set of default transformations will be applied to your dataset.
        - You can **customize the transformations** by visiting the **Data Transformation** section.
        - Once your dataset is transformed, you can **query your database using the LLM** to display visualizations.
    """)

    st.subheader("📊 Data Transformation")
    st.markdown("""
        - Go to the **Data Transformation** section.
        - Upload a dataset in **CSV, Excel, JSON, or PDF** format.
        - The app will **analyze your data** and display an overview.
        - You can perform the following transformations:
            - **Handle missing values**: Fill missing data with mean, median, or most frequent values, or drop them.
            - **Remove duplicates**: Choose whether to keep or delete duplicate rows.
            - **Handle outliers**: Apply transformations like logarithmic scaling or replace extreme values with mean/median.
        - Once the transformations are applied, you can **download the cleaned dataset**.
    """)

    st.subheader("ℹ️ About")
    st.markdown("""
        - Check the **About** page for more details on this project and its purpose.
    """)

    st.success("🚀 You are now ready to use the app! Select a section from the sidebar.")


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
    st.title("ℹ️ About QueryGenius")

    st.markdown("""
        **QueryGenius** is a powerful tool designed to simplify data transformations and make data analysis more accessible. The app leverages a **Large Language Model (LLM)** to provide intelligent insights and natural language querying capabilities.

        ### Developed By:
        - **Kabeda Hiba**: Hiba.kabada@dauphine.eu
        - **Inoubli Meriam**: Meriam.inoubli@dauphine.eu
                
        ### Under the guidance of:
        - **Professor Hadrien Mariaccia**
        
        
        ### Technologies Used:
        - **Large Language Model (LLM)**: Powers the chatbot and natural language processing.
        - **Streamlit**: Framework for building the interactive web interface.
        - **Pandas & Numpy**: For efficient data manipulation and analysis.
        - **Matplotlib & Seaborn**: Libraries for data visualization.
        - **PDFplumber**: Extracts data from PDF files for conversion to usable formats.

    """)

    st.markdown("""
        ---
        Made with ❤️
    """)

