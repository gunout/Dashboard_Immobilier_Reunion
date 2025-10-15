# dashboard_reunion_multi_communes.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import io
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Immobilier Réunion",
    page_icon="🏝️",
    layout="wide"
)

# --- Dictionnaire des communes de La Réunion (Code INSEE -> Nom) ---
# NOTE : La Réunion est divisée en 24 communes avec des codes INSEE de 97401 à 97424
COMMUNES_REUNION = {
    "97401": "Les Avirons",
    "97402": "Bras Panon",
    "97403": "Cilaos",
    "97404": "Entre-Deux",
    "97405": "L'Étang-Salé",
    "97406": "Petite-Île",
    "97407": "La Plaine-des-Palmistes",
    "97408": "Le Port",
    "97409": "La Possession",
    "97410": "Saint-André",
    "97411": "Saint-Benoît",
    "97412": "Saint-Denis",
    "97413": "Saint-Joseph",
    "97414": "Saint-Leu",
    "97415": "Saint-Louis",
    "97416": "Sainte-Marie",
    "97417": "Sainte-Rose",
    "97418": "Sainte-Suzanne",
    "97419": "Saint-Paul",
    "97420": "Saint-Philippe",
    "97421": "Saint-Pierre",
    "97422": "Salazie",
    "97423": "Le Tampon",
    "97424": "Trois-Bassins",
}

# Inverser le dictionnaire pour avoir Nom -> Code INSEE (plus pratique pour le selectbox)
NOMS_COMMUNES = {v: k for k, v in COMMUNES_REUNION.items()}

# --- Fonction de chargement des données (générique) ---
@st.cache_data
def load_commune_data(insee_code: str):
    """
    Charge les données DVF 2024 pour une commune de La Réunion donnée par son code INSEE.
    """
    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/2024/communes/974/{insee_code}.csv"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text), sep=',', low_memory=False)
        
        if df.empty:
            return pd.DataFrame()

        # Nettoyage (identique à la version précédente)
        df["date_mutation"] = pd.to_datetime(df["date_mutation"], format='%Y-%m-%d', errors='coerce')
        df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors='coerce')
        df = df[df["type_local"].isin(['Maison', 'Appartement'])]
        
        if df.empty:
            return pd.DataFrame()

        df = df.dropna(subset=["valeur_fonciere", "surface_reelle_bati", "code_postal", "date_mutation"])
        df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors='coerce')
        df = df.dropna(subset=["surface_reelle_bati"])

        if df.empty:
            return pd.DataFrame()

        df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
        # Ajustement des filtres pour La Réunion (prix au m² généralement plus bas qu'à Paris)
        df = df[(df['prix_m2'] > 100) & (df['prix_m2'] < 8000)]
        
        if df.empty:
            return pd.DataFrame()
        
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion pour la commune {insee_code} : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        return pd.DataFrame()

# --- Interface Utilisateur ---
st.title("🏝️ Dashboard Immobilier Réunion")

# Sélection de la commune dans la barre latérale
st.sidebar.header("Sélection de la commune")
selected_commune_name = st.sidebar.selectbox(
    "Choisissez une commune :",
    options=sorted(NOMS_COMMUNES.keys())
)

# Récupérer le code INSEE correspondant
selected_insee_code = NOMS_COMMUNES[selected_commune_name]

# Afficher un message d'information dynamique
st.info(f"ℹ️ Données réelles DVF 2024 pour la commune de **{selected_commune_name}** (INSEE {selected_insee_code}), provenant de data.gouv.fr")

# --- Chargement et Traitement des Données ---
df = load_commune_data(selected_insee_code)

if df.empty:
    st.warning(f"Aucune donnée de vente (Maison/Appartement) valide trouvée pour {selected_commune_name} en 2024.")
    st.stop()

# --- Filtres ---
st.sidebar.header("Filtres")
codes_postaux_disponibles = sorted(df['code_postal'].astype(str).unique())
code_postal_selectionne = st.sidebar.multiselect("Code postal", codes_postaux_disponibles, default=codes_postaux_disponibles)
type_local = st.sidebar.selectbox("Type de bien", ['Tous', 'Maison', 'Appartement'])
prix_min = st.sidebar.number_input("Prix minimum (€)", value=0, step=10000)
prix_max = st.sidebar.number_input("Prix maximum (€)", value=int(df['valeur_fonciere'].max()), step=10000)

# Application des filtres
df_filtre = df[
    (df['code_postal'].astype(str).isin(code_postal_selectionne)) &
    (df['valeur_fonciere'] >= prix_min) &
    (df['valeur_fonciere'] <= prix_max)
].copy()

if type_local != 'Tous':
    df_filtre = df_filtre[df_filtre['type_local'] == type_local]

if df_filtre.empty:
    st.warning("Aucune transaction ne correspond à vos filtres.")
    st.stop()

# --- KPIs et Visualisations ---
st.header(f"Indicateurs Clés pour {selected_commune_name}")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Prix Moyen / m²", f"{df_filtre['prix_m2'].mean():.0f} €")
with col2:
    st.metric("Prix Médian", f"{df_filtre['valeur_fonciere'].median():.0f} €")
with col3:
    st.metric("Transactions", f"{len(df_filtre):,}")
with col4:
    surface_moyenne = df_filtre['surface_reelle_bati'].mean()
    st.metric("Surface Moyenne", f"{surface_moyenne:.0f} m²")

st.header(f"Visualisations pour {selected_commune_name}")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Répartition des Prix au m²")
    fig = px.histogram(df_filtre, x='prix_m2', nbins=50, color='type_local', marginal="box")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Répartition des Types de Biens")
    fig = px.pie(df_filtre, names='type_local', title='Répartition par type')
    st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Carte des Transactions à {selected_commune_name}")
if 'latitude' in df_filtre.columns and 'longitude' in df_filtre.columns:
    df_carte = df_filtre.sample(min(5000, len(df_filtre)))
    fig = px.scatter_mapbox(df_carte, lat="latitude", lon="longitude", color="prix_m2", size="surface_reelle_bati", hover_data=["valeur_fonciere", "type_local", "date_mutation"], color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=10, mapbox_style="open-street-map", title=f"Carte de {len(df_carte)} transactions (échantillon)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Les données de localisation (latitude/longitude) ne sont pas disponibles pour afficher la carte.")

st.subheader("Détail des Transactions (dernières)")
st.dataframe(df_filtre.sort_values('date_mutation', ascending=False).head(100).drop(columns=['latitude', 'longitude'], errors='ignore'))