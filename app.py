"""
Application Streamlit - Assistant de Carrière
Interface principale et orchestration du pipeline
"""
import streamlit as st
import pandas as pd
from reliefweb_client import find_job_urls
from scraper import scrape_job_description
from gemini_analyzer import get_compatibility_analysis
from report_utils import generate_excel_export
from config import SEARCH_QUERIES
from credits import initialize_credits, show_credits_fixed_footer


# Configuration de la page
st.set_page_config(
    page_title="Assistant de Carrière",
    page_icon="💼",
    layout="wide"
)
# Initialiser les crédits dans la sidebar
#initialize_credits(location="sidebar", language="fr")

@st.cache_data(show_spinner=False)
def run_full_analysis(api_key: str, max_jobs: int = None):
    """
    Exécute le pipeline complet d'analyse des offres d'emploi.
    
    Args:
        api_key: Clé API Gemini
        max_jobs: Nombre maximum d'offres à analyser (None = toutes)
        
    Returns:
        Liste de dictionnaires contenant les résultats d'analyse
    """
    results = []
    
    # Étape 1: Recherche des URLs
    with st.spinner("🔍 Recherche des offres d'emploi sur ReliefWeb..."):
        job_urls = find_job_urls(SEARCH_QUERIES)
    
    if not job_urls:
        st.warning("Aucune offre d'emploi trouvée.")
        return results
    
    # Limiter le nombre d'offres si spécifié
    if max_jobs:
        job_urls = job_urls[:max_jobs]
    
    st.info(f"📊 {len(job_urls)} offres trouvées. Analyse en cours...")
    
    # Étape 2: Analyse de chaque offre
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, url in enumerate(job_urls):
        status_text.text(f"Analyse de l'offre {idx + 1}/{len(job_urls)}...")
        
        # Scraping
        job_text = scrape_job_description(url)
        
        if not job_text:
            st.warning(f"⚠️ Impossible de récupérer le contenu de: {url}")
            continue
        
        # Analyse avec Gemini
        analysis = get_compatibility_analysis(job_text, api_key)
        
        # Stocker les résultats
        result = {
            "URL": url,
            "Verdict": analysis["verdict"],
            "Score": analysis["score_pertinence"],
            "Analyse": analysis["analyse_succincte"],
            "Points Forts": ", ".join(analysis["points_forts"]),
            "Points Faibles": ", ".join(analysis["points_faibles"])
        }
        results.append(result)
        
        # Mise à jour de la barre de progression
        progress_bar.progress((idx + 1) / len(job_urls))
    
    progress_bar.empty()
    status_text.empty()
    
    return results


# Interface utilisateur
st.title("💼 Assistant de Carrière Intelligent")
st.markdown("Analyse automatique de compatibilité des offres d'emploi ReliefWeb")

# Barre latérale
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Clé API Gemini",
        type="password",
        help="Entrez votre clé API Google Gemini"
    )
    
    max_jobs = st.number_input(
        "Nombre max d'offres à analyser",
        min_value=1,
        max_value=100,
        value=10,
        help="Limiter le nombre d'offres pour un test rapide"
    )
    
    st.markdown("---")
    st.markdown("### 📋 Catégories de recherche")
    for category, queries in SEARCH_QUERIES.items():
        st.markdown(f"**{category}**")
        for query in queries:
            st.markdown(f"- {query}")

# Bouton principal
if st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Veuillez entrer votre clé API Gemini dans la barre latérale.")
    else:
        # Exécuter l'analyse
        results = run_full_analysis(api_key, max_jobs)
        
        if results:
            st.success(f"✅ Analyse terminée ! {len(results)} offres analysées.")
            
            # Afficher les résultats
            df = pd.DataFrame(results)
            
            # Tri par score décroissant
            df = df.sort_values("Score", ascending=False)
            
            # Affichage avec couleurs conditionnelles
            st.subheader("📊 Résultats de l'analyse")
            
            # Créer des onglets pour les différentes vues
            tab1, tab2, tab3 = st.tabs(["📋 Tableau complet", "✅ Compatibles", "📈 Statistiques"])
            
            with tab1:
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "URL": st.column_config.LinkColumn("Lien"),
                        "Score": st.column_config.ProgressColumn(
                            "Score",
                            format="%d",
                            min_value=0,
                            max_value=100
                        )
                    }
                )
            
            with tab2:
                compatibles = df[df["Verdict"].str.contains("COMPATIBLE", na=False)]
                st.write(f"**{len(compatibles)} offres compatibles trouvées**")
                st.dataframe(compatibles, use_container_width=True)
            
            with tab3:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score moyen", f"{df['Score'].mean():.1f}")
                with col2:
                    st.metric("Score maximum", f"{df['Score'].max():.0f}")
                with col3:
                    compatible_count = len(df[df["Verdict"] == "COMPATIBLE"])
                    st.metric("Taux de compatibilité", f"{compatible_count/len(df)*100:.1f}%")
            
            # Bouton d'export
            st.markdown("---")
            excel_data = generate_excel_export(df)
            st.download_button(
                label="📥 Télécharger les résultats (Excel)",
                data=excel_data,
                file_name="resultats_analyse_emploi.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Aucun résultat à afficher.")

# Instructions
with st.expander("ℹ️ Comment utiliser cette application"):
    st.markdown("""
    1. **Entrez votre clé API Gemini** dans la barre latérale
    2. **Ajustez le nombre maximum d'offres** à analyser (optionnel)
    3. **Cliquez sur "Lancer l'analyse"** pour démarrer
    4. **Consultez les résultats** dans les différents onglets
    5. **Téléchargez le rapport Excel** pour une analyse approfondie
    
    L'application recherche automatiquement les offres d'emploi sur ReliefWeb,
    les analyse avec l'IA Gemini, et vous fournit un verdict de compatibilité
    basé sur votre profil (configuré dans `config.py`).
    """)

# Footer avec crédits
show_credits_fixed_footer(language="fr")