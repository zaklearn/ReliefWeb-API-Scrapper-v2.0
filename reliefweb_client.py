"""
Client pour interagir avec l'API ReliefWeb
"""
import requests
import time
from typing import List, Dict


def find_job_urls(search_queries: Dict[str, List[str]]) -> List[str]:
    """
    Recherche des offres d'emploi sur ReliefWeb et retourne leurs URLs uniques.
    
    Args:
        search_queries: Dictionnaire de catégories avec listes de mots-clés
        
    Returns:
        Liste d'URLs uniques des offres d'emploi trouvées
    """
    # API V2 avec appname dans l'URL
    base_url = "https://api.reliefweb.int/v2/jobs?appname=career-assistant"
    all_urls = set()  # Utiliser un set pour éviter les doublons
    
    # Parcourir toutes les catégories et requêtes
    for category, queries in search_queries.items():
        for query in queries:
            print(f"Recherche pour: {query} (catégorie: {category})")
            
            offset = 0
            limit = 100  # Maximum par requête
            
            while True:
                try:
                    # Payload pour l'API ReliefWeb V2
                    payload = {
                        "query": {
                            "value": query,
                            "fields": ["title", "body"],
                            "operator": "OR"
                        },
                        "filter": {
                            "field": "status",
                            "value": "published"
                        },
                        "fields": {
                            "include": ["url", "title", "date"]
                        },
                        "limit": limit,
                        "offset": offset
                    }
                    
                    response = requests.post(base_url, json=payload, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    jobs = data.get("data", [])
                    
                    if not jobs:
                        break  # Plus de résultats
                    
                    # Extraire les URLs
                    for job in jobs:
                        url = job.get("fields", {}).get("url")
                        if url:
                            all_urls.add(url)
                    
                    # Vérifier s'il y a plus de résultats
                    total_count = data.get("totalCount", 0)
                    if offset + limit >= total_count:
                        break
                    
                    offset += limit
                    time.sleep(0.5)  # Pause pour respecter l'API
                    
                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors de la recherche pour '{query}': {e}")
                    break
    
    print(f"Total d'offres uniques trouvées: {len(all_urls)}")
    return list(all_urls)