"""
Module de scraping pour extraire le contenu des pages d'offres d'emploi
"""
import requests
from bs4 import BeautifulSoup


def scrape_job_description(url: str) -> str:
    """
    Extrait le contenu textuel d'une page d'offre d'emploi.
    
    Args:
        url: URL de la page à scraper
        
    Returns:
        Texte nettoyé de la page, ou chaîne vide en cas d'erreur
    """
    try:
        # Récupérer le contenu HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parser avec BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Supprimer les scripts et styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extraire le texte
        text = soup.get_text(separator=' ', strip=True)
        
        # Nettoyer les espaces multiples
        text = ' '.join(text.split())
        
        return text
        
    except requests.exceptions.Timeout:
        print(f"Timeout lors du scraping de {url}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {url}: {e}")
        return ""
    except Exception as e:
        print(f"Erreur inattendue lors du scraping de {url}: {e}")
        return ""