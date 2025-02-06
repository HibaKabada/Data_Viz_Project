import os
import pandas as pd
import numpy as np
import streamlit as st
import chardet
import pdfplumber
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore

# 📌 Fonction pour détecter l'encodage d'un fichier
def detect_encoding(file):
    raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

# 📌 Fonction pour charger le fichier et détecter l'encodage
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
            st.error("❌ Format non supporté. Veuillez télécharger un fichier CSV, Excel, JSON ou PDF.")
            return None

        return df

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du fichier : {str(e)}")
        return None


def pdf_to_dataframe(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        tables = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.append(pd.DataFrame(table[1:], columns=table[0]))
        return pd.concat(tables, ignore_index=True) if tables else None

# 📌 Fonction pour afficher un résumé détaillé des données
def summarize_data(df):
    st.subheader("📊 Résumé du jeu de données")

    col1, col2 = st.columns(2)  

    with col1:
        st.write("### 📋 Statistiques générales")
        summary_df = pd.DataFrame({
            "Statistique": ["Nombre de lignes", "Nombre de colonnes", "Valeurs manquantes", "Doublons"],
            "Valeur": [df.shape[0], df.shape[1], df.isnull().sum().sum(), df.duplicated().sum()]
        })
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

    with col2:
        st.write("### 📑 Types de données")
        dtype_df = pd.DataFrame({
            "Colonne": df.columns,
            "Type": df.dtypes.astype(str)
        })
        st.dataframe(dtype_df, hide_index=True, use_container_width=True)

    st.write("### 🔍 Aperçu des premières lignes")
    st.dataframe(df.head())

# 📌 Fonction pour gérer les valeurs manquantes
def handle_missing_values(df, strategy="mean"):
    if df.isnull().sum().sum() == 0:
        return df

    st.write(f"🛠 **Traitement des valeurs manquantes :** `{strategy}`")
    if strategy == "mean":
        df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
        df.fillna(df.select_dtypes(exclude=["number"]).mode().iloc[0], inplace=True)
    elif strategy == "median":
        df.fillna(df.select_dtypes(include=["number"]).median(), inplace=True)
        df.fillna(df.select_dtypes(exclude=["number"]).mode().iloc[0], inplace=True)
    elif strategy == "valeur la plus fréquente":
        df.fillna(df.mode().iloc[0], inplace=True)
    elif strategy == "drop":
        df.dropna(inplace=True)

    st.write("### 🔍 Aperçu après traitement des valeurs manquantes")
    st.dataframe(df.head())
    return df

# 📌 Fonction pour supprimer les doublons
def handle_duplicates(df, handle_dupes="Supprimer"):
    before = df.shape[0]

    if handle_dupes == "Supprimer":
        df = df.drop_duplicates()
        after = df.shape[0]
        st.write(f"🔄 **Suppression des doublons :** {before - after} lignes supprimées")
    else:
        st.write("✅ **Aucune suppression des doublons.** Les données restent inchangées.")

    st.write("### 🔍 Aperçu des données après traitement des doublons")
    st.dataframe(df.head())

    return df

# 📌 Fonction pour gérer les valeurs aberrantes avec choix de la stratégie
def handle_outliers(df, strategy="nothing", threshold=3):
    numeric_cols = df.select_dtypes(include=[np.number])
    if len(numeric_cols.columns) == 0:
        return df

    # Calcul des Z-scores pour identifier les valeurs aberrantes
    z_scores = np.abs(zscore(numeric_cols))
    outliers = (z_scores > threshold)

    if strategy == "nothing":
        st.write("🛠 **Aucune transformation appliquée aux valeurs aberrantes.**")
    else:
        if strategy == "log_transformation":
            st.write("🛠 **Application de la transformation logarithmique aux valeurs aberrantes.**")
            for col in numeric_cols.columns:
                df[col] = df[col].apply(lambda x: np.log(x + 1) if x > 0 else x)

        elif strategy == "mean":
            st.write("🛠 **Remplacement des valeurs aberrantes par la moyenne.**")
            for col in numeric_cols.columns:
                mean_val = df[col].mean()
                df.loc[outliers[col], col] = mean_val

        elif strategy == "median":
            st.write("🛠 **Remplacement des valeurs aberrantes par la médiane.**")
            for col in numeric_cols.columns:
                median_val = df[col].median()
                df.loc[outliers[col], col] = median_val

        elif strategy == "drop":
            st.write(f"🛠 **Suppression des lignes contenant des valeurs aberrantes.**")
            before = df.shape[0]
            df = df[~outliers.any(axis=1)]
            after = df.shape[0]
            st.write(f"🚀 **Valeurs aberrantes supprimées :** {before - after} lignes")

    # 📌 Sélection d'une colonne pour la visualisation
    selected_col = st.selectbox("📊 Sélectionnez une colonne à visualiser :", numeric_cols.columns)

    # 📊 Visualisation avant transformation
    st.write(f"### 📊 Distribution de `{selected_col}` avant traitement")
    fig, ax = plt.subplots(figsize=(8, 4))
    numeric_cols[selected_col].hist(bins=30, edgecolor="black", ax=ax)
    st.pyplot(fig)

    # 📊 Visualisation après transformation
    st.write(f"### 📊 Distribution de `{selected_col}` après traitement")
    fig, ax = plt.subplots(figsize=(8, 4))
    df[selected_col].hist(bins=30, edgecolor="black", ax=ax)
    st.pyplot(fig)

    # Aperçu des données après transformation
    st.write("### 🔍 Aperçu des données après traitement des valeurs aberrantes")
    st.dataframe(df.head())

    return df
# 📌 Interface utilisateur Streamlit
st.title("🔍 Analyse et Transformation des Données")
uploaded_file = st.file_uploader("📂 Téléchargez votre fichier", type=["csv", "xls", "xlsx", "json", "pdf"])

if uploaded_file:
    df = load_dataset(uploaded_file)
    if df is not None:
        summarize_data(df)

        # 🎛️ Choix des transformations
        st.subheader("🛠 Choix des corrections")
        handle_missing = st.radio("📌 Comment traiter les valeurs manquantes ?", ["mean", "median", "Valeur la plus fréquente", "drop"], index=0)

        # 📌 Application des transformations avec aperçu après chaque étape
        df = handle_missing_values(df, strategy=handle_missing)
        handle_dupes = st.radio("📌 Comment traiter les valeurs dupliquées ?", ["Supprimer", "Garder"], index=0)
        if handle_dupes:
            df = handle_duplicates(df, handle_dupes)
        
        # 🎛️ Choix du traitement des valeurs aberrantes
        outlier_strategy = st.selectbox("📌 Choisir le traitement des valeurs aberrantes :",
                                        ["nothing", "log_transformation", "mean", "median", "drop"], index=0)
        if outlier_strategy != "nothing":
            df = handle_outliers(df, strategy=outlier_strategy)
        
        # 📌 Affichage final des données transformées
        st.subheader("✅ Données transformées finales")
        st.dataframe(df.head())

        # 📤 Option pour télécharger le fichier transformé
        st.download_button(
            label="📥 Télécharger les données transformées",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="data_cleaned.csv",
            mime="text/csv"
        )