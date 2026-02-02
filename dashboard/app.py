"""Dashboard Streamlit pour visualisation."""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Emploi Store Dashboard", page_icon="💼", layout="wide")

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")


def fetch_data(endpoint: str) -> dict | None:
    """Récupère les données de l'API."""
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erreur de connexion à l'API: {e}")
        return None


def main() -> None:
    """Point d'entrée principal."""
    st.title("💼 Emploi Store Dashboard")
    st.markdown("Analyse des offres d'emploi France Travail")

    # Vérification de l'API
    health = fetch_data("health")
    if not health:
        st.error("❌ L'API n'est pas accessible. Démarrez-la avec `emploi-store api`")
        st.info("URL API: " + API_URL)
        return

    st.success("✅ API connectée")

    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Choisir une vue",
        [
            "📊 Vue d'ensemble",
            "💰 Salaires",
            "🎯 Compétences",
            "📍 Géographie",
            "📋 Liste des offres",
        ],
    )

    if page == "📊 Vue d'ensemble":
        show_overview()
    elif page == "💰 Salaires":
        show_salaries()
    elif page == "🎯 Compétences":
        show_skills()
    elif page == "📍 Géographie":
        show_geography()
    elif page == "📋 Liste des offres":
        show_offers_list()


def show_overview() -> None:
    """Affiche la vue d'ensemble."""
    st.header("📊 Vue d'ensemble")

    summary = fetch_data("stats/summary")
    if not summary:
        return

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Offres", summary.get("total_offers", 0))
    with col2:
        st.metric("Départements", summary.get("departments_with_offers", 0))
    with col3:
        st.metric("Dépts avec salaires", summary.get("avg_salary_by_dept", 0))
    with col4:
        st.metric("Top compétences", summary.get("top_skills_count", 0))

    # Distribution des contrats
    contracts = fetch_data("stats/contracts")
    if contracts:
        st.subheader("Distribution des types de contrat")
        df_contracts = pd.DataFrame(contracts)
        fig = px.pie(df_contracts, values="count", names="contract_type", title="Types de contrat")
        st.plotly_chart(fig, use_container_width=True)


def show_salaries() -> None:
    """Affiche les statistiques de salaire."""
    st.header("💰 Analyse des salaires")

    salaries = fetch_data("stats/salaries")
    if not salaries:
        st.info("Aucune donnée de salaire disponible")
        return

    df = pd.DataFrame(salaries)
    df = df.dropna(subset=["avg_min_salary", "avg_max_salary"])

    if df.empty:
        st.info("Pas assez de données de salaire pour afficher")
        return

    # Graphique des salaires par département
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["department_code"],
            y=df["avg_min_salary"],
            name="Salaire min moyen",
            marker_color="lightblue",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df["department_code"],
            y=df["avg_max_salary"],
            name="Salaire max moyen",
            marker_color="darkblue",
        )
    )

    fig.update_layout(
        title="Salaires moyens par département",
        xaxis_title="Département",
        yaxis_title="Salaire (€)",
        barmode="group",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tableau des données
    st.subheader("Données détaillées")
    st.dataframe(df.sort_values("avg_max_salary", ascending=False), use_container_width=True)


def show_skills() -> None:
    """Affiche les compétences."""
    st.header("🎯 Compétences demandées")

    limit = st.slider("Nombre de compétences", 5, 50, 20)
    skills = fetch_data(f"stats/skills?limit={limit}")

    if not skills:
        st.info("Aucune donnée de compétence disponible")
        return

    df = pd.DataFrame(skills)

    # Graphique en barres horizontal
    fig = px.bar(
        df,
        y="skill_name",
        x="count",
        orientation="h",
        title=f"Top {limit} compétences",
        labels={"skill_name": "Compétence", "count": "Nombre d'offres"},
    )
    fig.update_layout(height=600)

    st.plotly_chart(fig, use_container_width=True)

    # Tableau
    st.dataframe(df, use_container_width=True)


def show_geography() -> None:
    """Affiche la géographie."""
    st.header("📍 Répartition géographique")

    dept_data = fetch_data("stats/offers-by-department")
    if not dept_data:
        st.info("Aucune donnée géographique disponible")
        return

    df = pd.DataFrame(dept_data)

    # Camembert des offres par département
    fig = px.pie(
        df,
        values="count",
        names="department_code",
        title="Répartition des offres par département",
        hole=0.3,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Carte choroplèthe (simulation avec données)
    st.subheader("Carte des offres")
    st.info("Carte interactive disponible avec coordonnées GPS des offres")


def show_offers_list() -> None:
    """Affiche la liste des offres."""
    st.header("📋 Liste des offres")

    limit = st.slider("Nombre d'offres", 10, 500, 50)
    offers = fetch_data(f"offers?limit={limit}")

    if not offers:
        st.info("Aucune offre disponible")
        return

    df = pd.DataFrame(offers)

    # Filtres
    city_filter = "Tous"
    contract_filter = "Tous"
    col1, col2 = st.columns(2)
    with col1:
        if "city" in df.columns:
            cities = ["Tous"] + sorted(df["city"].dropna().unique().tolist())
            city_filter = st.selectbox("Ville", cities)
    with col2:
        if "contract_type" in df.columns:
            contracts = ["Tous"] + sorted(df["contract_type"].dropna().unique().tolist())
            contract_filter = st.selectbox("Type de contrat", contracts)

    # Application des filtres
    filtered_df = df.copy()
    if city_filter != "Tous":
        filtered_df = filtered_df[filtered_df["city"] == city_filter]
    if contract_filter != "Tous":
        filtered_df = filtered_df[filtered_df["contract_type"] == contract_filter]

    st.write(f"{len(filtered_df)} offres affichées")
    st.dataframe(filtered_df, use_container_width=True)

    # Détails d'une offre
    st.subheader("Détails d'une offre")
    offer_id = st.text_input("ID de l'offre", "")
    if offer_id:
        offer = fetch_data(f"offers/{offer_id}")
        if offer:
            st.json(offer)
        else:
            st.error("Offre non trouvée")


if __name__ == "__main__":
    main()
