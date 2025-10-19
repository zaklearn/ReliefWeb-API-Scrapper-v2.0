"""
Module d'analyse de compatibilité avec l'API Gemini
"""
import google.generativeai as genai
import json
from config import CANDIDATE_PROFILE


def get_compatibility_analysis(job_description: str, api_key: str) -> dict:
    """
    Analyse la compatibilité entre le profil candidat et une offre d'emploi.
    
    Args:
        job_description: Texte complet de l'offre d'emploi
        api_key: Clé API Gemini
        
    Returns:
        Dictionnaire contenant l'analyse de compatibilité
    """
    try:
        # Configuration du client Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Construction du prompt
        prompt = f"""
Tu es un expert en recrutement. Analyse la compatibilité entre ce profil de candidat et cette offre d'emploi.

PROFIL DU CANDIDAT:
{CANDIDATE_PROFILE}

OFFRE D'EMPLOI:
{job_description[:8000]}

Fournis une analyse de compatibilité UNIQUEMENT au format JSON suivant (sans texte avant ou après):
{{
    "verdict": "COMPATIBLE" ou "NON COMPATIBLE" ou "MOYENNEMENT COMPATIBLE",
    "score_pertinence": <nombre entre 0 et 100>,
    "analyse_succincte": "<résumé en 2-3 phrases>",
    "points_forts": ["point1", "point2", "point3"],
    "points_faibles": ["point1", "point2"]
}}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""
        
        # Appel à l'API
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Nettoyer la réponse (enlever les markdown code blocks si présents)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parser le JSON
        analysis = json.loads(response_text)
        
        # Valider la structure
        required_keys = ["verdict", "score_pertinence", "analyse_succincte", 
                        "points_forts", "points_faibles"]
        if not all(key in analysis for key in required_keys):
            raise ValueError("Réponse JSON incomplète de l'API")
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"Erreur de parsing JSON: {e}")
        return {
            "verdict": "ERREUR",
            "score_pertinence": 0,
            "analyse_succincte": "Erreur lors de l'analyse de la réponse",
            "points_forts": [],
            "points_faibles": ["Erreur d'analyse"]
        }
    except Exception as e:
        print(f"Erreur lors de l'analyse Gemini: {e}")
        return {
            "verdict": "ERREUR",
            "score_pertinence": 0,
            "analyse_succincte": f"Erreur: {str(e)}",
            "points_forts": [],
            "points_faibles": ["Erreur technique"]
        }