import streamlit as st
import pandas as pd
import anthropic  
import os
import matplotlib.pyplot as plt
import re
from dotenv import load_dotenv

# Load environment variables (API key)
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)

# Helper function to interact with Claude API
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

# Analyze the user query: Identify what type of question is being asked about the dataset
def analyze_query(user_request: str) -> str:
    """
    Analyzes the user request and provides a summary of what data is involved and what visualization is needed.
    """
    prompt = f"""
    Given the user's request, summarize the following:
    - What is the specific question about the dataset (e.g., trends, distributions, comparisons)?
    - What type of data is involved (categorical, numerical, time-series)?
    - What key insights or visualizations should be provided to answer the question?

    User Request:
    "{user_request}"
    """
    return query_claude(prompt)

# Select appropriate visualizations based on the dataset and question
def select_best_visualization(data: pd.DataFrame, user_request: str) -> str:
    """
    Based on the dataset summary and the user's request, recommend the three most effective visualization techniques while ensuring compliance with data visualization best practices:
    """
    dataset_summary = data.describe(include='all').to_string()
    prompt = f"""
    Based on the dataset summary and the user's request, recommend the three most effective visualization techniques while ensuring compliance with data visualization best practices:
    -Clearly specify the type of visualization (e.g., line chart, bar chart, heatmap, box plot).
    -Justify why each visualization is the most suitable choice given the dataset and the analytical goal.
    -Consider factors like data clarity, ease of interpretation, and suitability for large datasets.
    -If applicable, suggest enhancements like color schemes, annotations, or interactive elements that improve user experience.
    
    Dataset Summary:
    {dataset_summary}

    User Request:
    {user_request}

    Provide a list of 3 visualization types that are most suited for answering this question.
    """
    return query_claude(prompt)

# Generate Python code for the selected visualization types
def generate_visualization_code(data: pd.DataFrame, visualization_types: str, user_request: str) -> str:
    """
    Based on the user's request and dataset, generate Python code to implement the selected visualizations.
    """
    dataset_info = data.dtypes.to_string()
    prompt = f"""
    Based on the dataset and user request, generate Python code for the following visualizations using matplotlib, seaborn, or plotly:
    - {visualization_types}

    Dataset Columns and Types:
    {dataset_info}

    User Request:
    {user_request}

    Guidelines:
    -Use the DataFrame variable name df.
    -The code should be optimized for Streamlit and ensure clear, precise, and well-structured visualizations.
    -Apply appropriate titles, axis labels, legends, and color schemes for readability.
    -Use gridlines, annotations, and formatting enhancements where relevant.
    -Ensure the code is executable without requiring modifications.
    -Return only the Python code; do not include explanations.
    """
    return query_claude(prompt)

# Explain why specific visualizations are appropriate for the user's request
def explain_visualization_choice(visualization_types: str, user_request: str) -> str:
    """
    Explain why each of the following visualizations is the best choice for answering the user's question, ensuring clarity and alignment with best practices:
    Provides an interpretation of each visualization and how it helps in answering the question.
    """
    prompt = f"""
    Provide a brief but precise explanation for each visualization.
    Clearly describe what insights each visualization will reveal.
    For each visualization, explain how it answers the specific question posed by the user and the insights it provides. 
    Interpret the visualizations in the context of the dataset and the user's request.
    
    Visualization Types: {visualization_types}

    User Request:
    {user_request}
    """
    return query_claude(prompt)

# Main Streamlit interface for chatbot
def chatbot_interface():
    """
    Streamlit interface for uploading datasets and interacting with the chatbot.
    """
    st.set_page_config(page_title="📊 AI Chatbot for Data Visualization", layout="wide")
    st.title("🤖 AI Chatbot for Smart Data Visualizations")

    # File upload section
    uploaded_file = st.file_uploader("📂 Upload a CSV or Excel file", type=["csv", "xlsx"], key="file_upload")

    if uploaded_file:
        # Load dataset
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.dataframe(df.head())  # Display the first few rows of the dataset

        # User request for visualization
        user_request = st.text_area("📝 Describe the visualization you want:", placeholder="Example: Show a trend of sales over time using a line chart")

        if st.button("🚀 Generate Visualization"):
            with st.spinner("⏳ Processing your request..."):
                # Analyze the user's query
                query_analysis = analyze_query(user_request)
                best_viz = select_best_visualization(df, user_request)
                explanation = explain_visualization_choice(best_viz, user_request)
                code = generate_visualization_code(df, best_viz, user_request)

                # Display results with improved structure
                st.subheader("🔍 Query Analysis")
                st.write("### Key Insights")
                st.write(query_analysis)

                st.subheader("📊 Selected Visualizations: ")
                st.write(f"### Suggested Visualizations: {best_viz}")
                st.write("#### Why These Visualizations Are Chosen:")
                st.write(explanation)

                st.subheader("🖥 Generated Python Code")
                st.code(code, language="python")
                
                # Execute the visualization code in Streamlit
                try:
                    match = re.search(r"```python\n(.*?)\n```", code, re.DOTALL)
                    python_code = match.group(1) if match else code
                    python_code = python_code.replace("plt.show()", "st.pyplot(plt)")  # Ensure Streamlit compatibility
                    exec(python_code, globals())  # Execute the generated code
                    
                except Exception as e:
                    st.error(f"⚠️ Error executing visualization: {e}")

    else:
        st.info("📂 Upload a file to get started!")

# Run the app
if __name__ == "__main__":
    chatbot_interface()
