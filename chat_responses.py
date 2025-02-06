import streamlit as st
import pandas as pd
import anthropic  
import os
import matplotlib.pyplot as plt
import re
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)


def query_claude(prompt: str) -> str:
    """
    Sends a request to Claude (Anthropic) API and returns the response.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8000
    )
    return response.content[0].text.strip()


def analyze_query(user_request: str) -> str:
    """
    Uses Claude to understand the user's visualization request and summarize key details.
    """
    prompt = f"""
    You are an expert AI assistant specializing in data visualization. Given the following user request, summarize it with:
    - What type of data is involved? (Numerical, categorical, time-series, etc.)
    
    Ensure that the answer is clear and directly addresses both data type and visualization choice.

    User Request:
    "{user_request}"
    """
    return query_claude(prompt)


def select_best_visualization(data: pd.DataFrame, user_request: str) -> str:
    """
    Uses Claude to determine the best visualization based on the dataset and user request.
    """
    dataset_summary = data.describe(include='all').to_string()
    prompt = f"""
    You are an expert in data visualization. Based on the following dataset summary and user request, 
    suggest the most appropriate visualization type. Choose only one visualization and do not generate any Python code.
    - What is the best type of visualization for this request? 

    Dataset Summary:
    {dataset_summary}

    User Request:
    {user_request}

    Respond with only the name of the visualization that fits the request best.
    """
    return query_claude(prompt)


def generate_visualization_code(data: pd.DataFrame, visualization_type: str, user_request: str) -> str:
    """
    Uses Claude to generate Python code for the selected visualization.
    """
    dataset_info = data.dtypes.to_string()
    prompt = f"""
    You are an expert Python programmer. Based on the following dataset and the user request, generate Python code using `matplotlib`, `seaborn`, or `plotly` to create a {visualization_type}.

    Dataset Columns and Types:
    {dataset_info}

    User Request:
    {user_request}

    Guidelines:
    - Assume the DataFrame is named `df`.
    - The code should work in a Streamlit app.
    - Do not explain or provide anything other than the Python code.
    """
    return query_claude(prompt)


def explain_visualization_choice(visualization_type: str, user_request: str) -> str:
    """
    Uses Claude to explain why a certain visualization was chosen.
    """
    prompt = f"""
    Explain in a few sentences why a {visualization_type} is the best choice for the following user request. Keep it clear, simple, and under 3 sentences.

    User Request:
    {user_request}
    """
    return query_claude(prompt)


def chatbot_interface():
    """
    Streamlit interface for the chatbot.
    """
    st.set_page_config(page_title="📊 AI Chatbot for Data Visualization", layout="wide")
    st.title("🤖 AI Chatbot for Smart Data Visualizations")

    uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"], key="file_upload")

    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.dataframe(df.head())

        user_request = st.text_area("📝 Describe the visualization you want:",
                                    placeholder="Example: Show a trend of sales over time using a line chart")

        if st.button("🚀 Generate Visualization"):
            with st.spinner("⏳ Processing your request..."):
                query_analysis = analyze_query(user_request)
                best_viz = select_best_visualization(df, user_request)
                explanation = explain_visualization_choice(best_viz, user_request)
                code = generate_visualization_code(df, best_viz, user_request)

                st.subheader("🔍 Query Analysis")
                st.write(query_analysis)

                st.subheader("📊 Selected Visualization: " + best_viz)
                st.write(explanation)

                st.subheader("🖥 Generated Python Code")
                st.code(code, language="python")
                
                try:
                    match = re.search(r"```python\n(.*?)\n```", code, re.DOTALL)
                    python_code = match.group(1) if match else code
                    python_code = python_code.replace("plt.show()", "st.pyplot(plt)")
                    exec(python_code, globals())  
                    
                except Exception as e:
                    st.error(f"⚠️ Error executing visualization: {e}")
                    logger.error(f"⚠️ Error executing visualization: {e}")

    else:
        st.info("📂 Upload a file to get started!")

if __name__ == "__main__":
    chatbot_interface()
