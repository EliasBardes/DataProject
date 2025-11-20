import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path


def format_period_to_french(period):
    mois_fr = {
        1: "janvier",
        2: "février",
        3: "mars",
        4: "avril",
        5: "mai",
        6: "juin",
        7: "juillet",
        8: "août",
        9: "septembre",
        10: "octobre",
        11: "novembre",
        12: "décembre",
    }
    return f"{mois_fr.get(period.month, 'Inconnu')} {period.year}"

# Charger les données (ajustez le chemin si nécessaire)
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / 'data_activity.csv'
    try:
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])  # Convertir la colonne date
        return df
    except FileNotFoundError:
        st.error("Le fichier 'data_activity.csv' est introuvable. Veuillez vérifier le chemin.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error("Le fichier 'data_activity.csv' est vide. Veuillez vérifier son contenu.")
        return pd.DataFrame()

df = load_data()

if st.button("🔄 Recharger les données"):
    load_data.clear()
    df = load_data()
    st.success("Jeu de données rafraîchi.")


def generate_digest_data(user_id, df_input):
    """
    Génère un résumé des données d'activité pour un utilisateur donné.
    
    Args:
        user_id: ID de l'utilisateur
        df_input: DataFrame contenant les données d'activité
    
    Returns:
        Dictionnaire contenant les KPI et statistiques de l'utilisateur
    """
    # 1. Filtrer les données pour l'utilisateur
    df_user = df_input[df_input['user_id'] == user_id].copy()

    if df_user.empty:
        return None  # Aucun utilisateur trouvé

    # 2. CALCUL DES KPI
    total_time_min = df_user['time_spent_min'].sum()
    total_time_hrs = round(total_time_min / 60, 1)

    # Top 3 des fonctionnalités
    top_actions = df_user['action_type'].value_counts().head(3).reset_index()
    top_actions.columns = ['action', 'count']

    # Mois le plus actif
    df_user['month'] = df_user['date'].dt.to_period('M')
    active_period = df_user['month'].value_counts().idxmax()
    active_month = format_period_to_french(active_period)

    return {
        'total_time_hrs': total_time_hrs,
        'top_actions': top_actions,
        'active_month': active_month,
        'df_actions_count': df_user['action_type'].value_counts(),
        'df_user': df_user
    }


# Interface Streamlit
st.title("📊 Tableau de bord d'analyse Jamespot")

if not df.empty:
    # Sélecteur d'utilisateur
    user_ids = df['user_id'].unique().tolist()
    selected_user = st.selectbox("Sélectionnez un utilisateur", user_ids)
    
    if selected_user:
        # Générer les données du digest
        digest = generate_digest_data(selected_user, df)
        
        if digest:
            # Afficher les KPI
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Temps total", f"{digest['total_time_hrs']} heures")
            
            with col2:
                st.metric("Mois le plus actif", digest['active_month'])
            
            with col3:
                st.metric("Nombre d'actions", len(digest['df_actions_count']))
            
            # Top 3 des actions
            st.subheader("Top 3 des fonctionnalités utilisées")
            top_actions_df = digest['top_actions'].rename(
                columns={'action': 'Action', 'count': "Nombre d'occurrences"}
            )
            st.dataframe(top_actions_df, use_container_width=True)
            st.caption("Liste des trois fonctionnalités les plus utilisées par l'utilisateur sélectionné.")
            
            # Graphique des actions
            st.subheader("Répartition des actions")
            action_counts = (
                digest['df_actions_count']
                .rename_axis('Action')
                .reset_index(name="Occurrences")
            )
            chart = (
                alt.Chart(action_counts)
                .mark_arc(innerRadius=70, cornerRadius=8, stroke="#0f172a", strokeWidth=1)
                .encode(
                    theta=alt.Theta("Occurrences:Q", stack=True, title="Poids relatif"),
                    color=alt.Color(
                        "Action:N",
                        scale=alt.Scale(scheme="tableau20"),
                        legend=alt.Legend(title="Type d'action")
                    ),
                    tooltip=["Action", "Occurrences"]
                )
                .properties(height=420)
            )
            chart = alt.layer(chart).configure_legend(
                orient="right",
                labelColor="#e2e8f0",
                titleColor="#f8fafc",
            ).configure_view(
                strokeOpacity=0
            ).configure_title(color="#f8fafc")

            st.altair_chart(chart, use_container_width=True)
            st.caption("Diagramme en anneau indiquant la répartition des actions pour l'utilisateur.")

            st.divider()

            st.subheader("Options d'affichage détaillé")
            col_details, col_global = st.columns(2)
            with col_details:
                show_user_data = st.checkbox("Afficher toutes les données de l'utilisateur", value=False)
            with col_global:
                show_all_data = st.checkbox("Afficher toutes les données globales", value=False)

            if show_user_data:
                st.markdown("### Données complètes de l'utilisateur sélectionné")
                df_user_display = digest['df_user'][['date', 'action_type', 'time_spent_min', 'category']].rename(
                    columns={
                        'date': 'Date',
                        'action_type': "Type d'action",
                        'time_spent_min': 'Temps passé (minutes)',
                        'category': 'Catégorie'
                    }
                )
                st.dataframe(df_user_display, use_container_width=True)
                st.caption("Tableau détaillé listant chaque action réalisée par l'utilisateur sélectionné.")

            if show_all_data:
                st.markdown("### Données complètes du jeu de données")
                df_global_display = df.rename(
                    columns={
                        'user_id': 'Utilisateur',
                        'date': 'Date',
                        'action_type': "Type d'action",
                        'time_spent_min': 'Temps passé (minutes)',
                        'category': 'Catégorie'
                    }
                )
                st.dataframe(df_global_display, use_container_width=True)
                st.caption("Tableau complet contenant toutes les actions présentes dans le fichier de données.")
        else:
            st.warning(f"Aucune donnée trouvée pour l'utilisateur {selected_user}")
else:
    st.info("Aucune donnée disponible. Veuillez charger un fichier CSV valide.")
