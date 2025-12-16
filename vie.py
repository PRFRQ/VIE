<<<<<<< Updated upstream
#!/usr/bin/python3

import requests
import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env
load_dotenv()

#---------------CONFIGURATION---------------
# Configuration Discord Webhook (depuis variable d'environnement)
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

if not DISCORD_WEBHOOK_URL:
    print("❌ ERREUR: La variable d'environnement DISCORD_WEBHOOK_URL n est pas definie")
    print("💡 Creez un fichier .env a partir de .env.example et configurez votre webhook")
    exit(1)

# Chemins de fichiers (relatif au script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IDS_FILE = os.path.join(SCRIPT_DIR, 'ids.txt')

# Configuration API
API_BASE_URL = "https://civiweb-api-prd.azurewebsites.net/api"
API_SEARCH_URL = f"{API_BASE_URL}/Offers/search"
API_DETAILS_URL = f"{API_BASE_URL}/Offers/details"

#---------------FONCTIONS---------------
def log(message):
    """Affiche un message avec timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_existing_ids(filename):
    """Recupere les VIE deja connus depuis le fichier"""
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        log(f"Fichier {filename} non trouve, creation d un nouveau fichier")
        return set()

def write_new_ids(filename, ids):
    """Sauvegarde les nouveaux VIE dans le fichier"""
    with open(filename, 'a') as f:
        for id in ids:
            f.write(f'{id}\n')

def format_date(date_string):
    """Formate une date ISO en format lisible (YYYY-MM-DD)"""
    if not date_string:
        return "N/A"
    try:
        return date_string.split('T')[0]
    except:
        return date_string

def clean_contact_name(contact_name):
    """Nettoie le nom du contact pour LinkedIn"""
    if not contact_name:
        return ""
    contact_name = contact_name.strip()
    # Supprime les civilites
    contact_name = re.sub(r'^(Madame|Monsieur)\s+', '', contact_name, flags=re.IGNORECASE)
    contact_name = contact_name.strip()
    return contact_name.replace(' ', '%20')

def get_offer_details(offer_id):
    try:
        url = f"{API_DETAILS_URL}/{offer_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log(f"Erreur lors de la recuperation des details de l offre {offer_id}: {e}")
        return None

def send_discord_notification(offer_data):
    """Envoie une notification Discord pour une nouvelle offre"""
    try:
        offer_id = str(offer_data['id'])
        contact_name = clean_contact_name(offer_data.get('contactName', ''))
        linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={contact_name}" if contact_name else "N/A"
        businessfrance_url = f"https://mon-vie-via.businessfrance.fr/offres/{offer_id}"
        
        # Prepare le contenu de la notification
        content = {
            "embeds": [
                {
                    "title": offer_data.get('missionTitle', 'Sans titre'),
                    "fields": [
                        {
                            "name": "🏭 Entreprise",
                            "value": offer_data.get('organizationName', 'N/A'),
                            "inline": True
                        },
                        {
                            "name": "�️ Pays",
                            "value": offer_data.get('countryName', 'N/A'),
                            "inline": True
                        },
                        {
                            "name": "🏙️ Ville",
                            "value": offer_data.get('cityName', 'N/A').strip() if offer_data.get('cityName') else 'N/A',
                            "inline": True
                        },
                        {
                            "name": "📅 Durée (mois)",
                            "value": str(offer_data.get('missionDuration', 'N/A')),
                            "inline": True
                        },
                        {
                            "name": "🎬 Début",
                            "value": format_date(offer_data.get('missionStartDate')),
                            "inline": True
                        },
                        {
                            "name": "🏁 Fin",
                            "value": format_date(offer_data.get('missionEndDate')),
                            "inline": True
                        },
                        {
                            "name": "📧 Email",
                            "value": offer_data.get('contactEmail', 'N/A'),
                            "inline": True
                        },
                        {
                            "name": "🌐 Business France",
                            "value": f"[Voir Offre]({businessfrance_url})",
                            "inline": True
                        },
                        {
                            "name": "🔗 LinkedIn",
                            "value": f"[Rechercher Contact]({linkedin_url})" if contact_name else "N/A",
                            "inline": True
                        },
                        {
                            "name": "💼 Télétravail",
                            "value": "✅ Oui" if offer_data.get('teleworkingAvailable') else "❌ Non",
                            "inline": True
                        },
                        {
                            "name": "📆 Date de publication",
                            "value": format_date(offer_data.get('creationDate')),
                            "inline": True
                        }
                    ],
                    "color": 3447003,  # Bleu
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(content),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        log(f"✅ Notification envoyée pour l'offre {offer_id}")
        return True
    except Exception as e:
        log(f"❌ Erreur lors de l'envoi de la notification Discord: {e}")
        return False

#---------------SCRIPT PRINCIPAL---------------
log("🔍 Début de la recherche de nouvelles offres VIE")

# Configuration de la recherche
# limit = nombre d'offres, query = mot cle, missionsDurations = durée VIE, geographicZones = continents
payload = {
    "limit": int(os.getenv('SEARCH_LIMIT', 1000)),
    "skip": 0,
    "latest": ["true"],  # Récupérer les dernières offres
    "query": os.getenv('SEARCH_QUERY', 'engineer'),
    "missionsDurations": [],
    "geographicZones": ["2", "3", "4", "6", "5", "8"],  # Tous les continents
    "activitySectorId": [],
    "missionsTypesIds": [],
    "countriesIds": [],
    "studiesLevelId": [],
    "companiesSizes": [],
    "specializationsIds": [],
    "entreprisesIds": [0],
    "missionStartDate": None
}

# Envoi de la requête de recherche
try:
    log(f"📡 Interrogation de l'API: {API_SEARCH_URL}")
    response = requests.post(
        API_SEARCH_URL,
        data=json.dumps(payload),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://mon-vie-via.businessfrance.fr',
            'Referer': 'https://mon-vie-via.businessfrance.fr/',
            'User-Agent': 'Mozilla/5.0'
        },
        timeout=30
    )
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    log(f"❌ Erreur lors de la requête API: {e}")
    exit(1)

# Traitement de la réponse
if response.status_code == 200:
    data = response.json()
    total_count = data.get('count', 0)
    log(f"📊 Total d'offres correspondantes: {total_count}")
    
    # Extraction des IDs des offres
    offers = data.get('result', [])
    if not offers:
        log("ℹ️ Aucune offre trouvée")
        exit(0)
    
    ids = [item['id'] for item in offers]
    log(f"📋 {len(ids)} offres récupérées")
    
    # Récupération des IDs déjà connus
    existing_ids = get_existing_ids(IDS_FILE)
    log(f"💾 {len(existing_ids)} offres déjà connues")
    
    # Identification des nouvelles offres
    new_ids = [id for id in ids if str(id) not in existing_ids]
    
    if new_ids:
        log(f"🆕 {len(new_ids)} nouvelle(s) offre(s) détectée(s): {new_ids}")
        
        # Traitement de chaque nouvelle offre
        success_count = 0
        for new_id in new_ids:
            log(f"📝 Traitement de l'offre {new_id}...")
            
            # Récupération des détails
            offer_details = get_offer_details(new_id)
            
            if offer_details:
                # Envoi de la notification Discord
                if send_discord_notification(offer_details):
                    success_count += 1
            else:
                log(f"⚠️ Impossible de récupérer les détails de l'offre {new_id}")
        
        # Sauvegarde des nouveaux IDs
        write_new_ids(IDS_FILE, new_ids)
        log(f"💾 {len(new_ids)} ID(s) sauvegardé(s) dans {IDS_FILE}")
        log(f"✅ {success_count}/{len(new_ids)} notification(s) envoyée(s) avec succès")
    else:
        log("ℹ️ Aucune nouvelle offre trouvée")

else:
    log(f"❌ La requête API a échoué avec le code {response.status_code}")
    exit(1)

log("✅ Recherche terminée")
=======
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import re
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env
load_dotenv()

#---------------CONFIGURATION---------------
# Configuration Discord Webhook (depuis variable d'environnement)
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

if not DISCORD_WEBHOOK_URL:
    print("[ERREUR] La variable d'environnement DISCORD_WEBHOOK_URL n'est pas definie")
    print("[INFO] Creez un fichier .env a partir de .env.example et configurez votre webhook")
    exit(1)

# Chemins de fichiers (relatif au script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IDS_FILE = os.path.join(SCRIPT_DIR, 'ids.txt')

# Configuration API
API_BASE_URL = "https://civiweb-api-prd.azurewebsites.net/api"
API_SEARCH_URL = f"{API_BASE_URL}/Offers/search"
API_DETAILS_URL = f"{API_BASE_URL}/Offers/details"

#---------------FONCTIONS---------------
def log(message):
    """Affiche un message avec timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_existing_ids(filename):
    """Récupère les VIE déjà connus depuis le fichier"""
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        log(f"Fichier {filename} non trouvé, création d'un nouveau fichier")
        return set()

def write_new_ids(filename, ids):
    """Sauvegarde les nouveaux VIE dans le fichier"""
    with open(filename, 'a') as f:
        for id in ids:
            f.write(f'{id}\n')

def format_date(date_string):
    """Formate une date ISO en format lisible (YYYY-MM-DD)"""
    if not date_string:
        return "N/A"
    try:
        return date_string.split('T')[0]
    except:
        return date_string

def clean_contact_name(contact_name):
    """Nettoie le nom du contact pour LinkedIn"""
    if not contact_name:
        return ""
    contact_name = contact_name.strip()
    # Supprime les civilités
    contact_name = re.sub(r'^(Madame|Monsieur)\s+', '', contact_name, flags=re.IGNORECASE)
    contact_name = contact_name.strip()
    return contact_name.replace(' ', '%20')

def get_offer_details(offer_id):
    """Récupère les détails d'une offre via l'API"""
    try:
        url = f"{API_DETAILS_URL}/{offer_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log(f"Erreur lors de la récupération des détails de l'offre {offer_id}: {e}")
        return None

def send_discord_notification(offer_data):
    """Envoie une notification Discord pour une nouvelle offre"""
    try:
        offer_id = str(offer_data['id'])
        contact_name = clean_contact_name(offer_data.get('contactName', ''))
        linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={contact_name}" if contact_name else "N/A"
        businessfrance_url = f"https://mon-vie-via.businessfrance.fr/offres/{offer_id}"
        
        # Prépare le contenu de la notification
        content = {
            "embeds": [
                {
                    "title": offer_data.get('missionTitle', 'Sans titre'),
                    "fields": [
                        {
                            "name": "🏭 Entreprise",
                            "value": offer_data.get('organizationName', 'N/A'),
                            "inline": True
                        },
                        {
                            "name": "🌍 Pays",
                            "value": offer_data.get('countryName', 'N/A'),
                            "inline": True
                        },
                        {
                            "name": "🏙️ Ville",
                            "value": offer_data.get('cityName', 'N/A').strip() if offer_data.get('cityName') else 'N/A',
                            "inline": True
                        },
                        {
                            "name": "📅 Durée (mois)",
                            "value": str(offer_data.get('missionDuration', 'N/A')),
                            "inline": True
                        },
                        {
                            "name": "🎬 Début",
                            "value": format_date(offer_data.get('missionStartDate')),
                            "inline": True
                        },
                        {
                            "name": "🏁 Fin",
                            "value": format_date(offer_data.get('missionEndDate')),
                            "inline": True
                        },
                        {
                            "name": "📧 Email",
                            "value": offer_data.get('contactEmail', 'N/A'),
                            "inline": True
                        },
                        {
                            "name": "🌐 Business France",
                            "value": f"[Voir Offre]({businessfrance_url})",
                            "inline": True
                        },
                        {
                            "name": "🔗 LinkedIn",
                            "value": f"[Rechercher Contact]({linkedin_url})" if contact_name else "N/A",
                            "inline": True
                        },
                        {
                            "name": "💼 Télétravail",
                            "value": "✅ Oui" if offer_data.get('teleworkingAvailable') else "❌ Non",
                            "inline": True
                        },
                        {
                            "name": "📆 Date de publication",
                            "value": format_date(offer_data.get('creationDate')),
                            "inline": True
                        }
                    ],
                    "color": 3447003,  # Bleu
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(content),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        log(f"[OK] Notification envoyee pour l'offre {offer_id}")
        return True
    except Exception as e:
        log(f"[ERREUR] Erreur lors de l'envoi de la notification Discord: {e}")
        return False

#---------------SCRIPT PRINCIPAL---------------
log("[START] Debut de la recherche de nouvelles offres VIE")

# Configuration de la recherche
# limit = nombre d'offres, query = mot clé, missionsDurations = durée VIE, geographicZones = continents
payload = {
    "limit": int(os.getenv('SEARCH_LIMIT', 1000)),
    "skip": 0,
    "latest": ["true"],  # Récupérer les dernières offres
    "query": os.getenv('SEARCH_QUERY', 'engineer'),
    "missionsDurations": [],
    "geographicZones": ["2", "3", "4", "6", "5", "8"],  # Tous les continents
    "activitySectorId": [],
    "missionsTypesIds": [],
    "countriesIds": [],
    "studiesLevelId": [],
    "companiesSizes": [],
    "specializationsIds": [],
    "entreprisesIds": [0],
    "missionStartDate": None
}

# Envoi de la requete de recherche
try:
    log(f"[API] Interrogation de l'API: {API_SEARCH_URL}")
    response = requests.post(
        API_SEARCH_URL,
        data=json.dumps(payload),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://mon-vie-via.businessfrance.fr',
            'Referer': 'https://mon-vie-via.businessfrance.fr/',
            'User-Agent': 'Mozilla/5.0'
        },
        timeout=30
    )
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    log(f"[ERREUR] Erreur lors de la requete API: {e}")
    exit(1)

# Traitement de la réponse
if response.status_code == 200:
    data = response.json()
    total_count = data.get('count', 0)
    log(f"[STATS] Total d'offres correspondantes: {total_count}")
    
    # Extraction des IDs des offres
    offers = data.get('result', [])
    if not offers:
        log("[INFO] Aucune offre trouvee")
        exit(0)
    
    ids = [item['id'] for item in offers]
    log(f"[STATS] {len(ids)} offres recuperees")
    
    # Recuperation des IDs deja connus
    existing_ids = get_existing_ids(IDS_FILE)
    log(f"[STATS] {len(existing_ids)} offres deja connues")
    
    # Identification des nouvelles offres
    new_ids = [id for id in ids if str(id) not in existing_ids]
    
    if new_ids:
        log(f"[NEW] {len(new_ids)} nouvelle(s) offre(s) detectee(s): {new_ids}")
        
        # Traitement de chaque nouvelle offre
        success_count = 0
        for idx, new_id in enumerate(new_ids, 1):
            log(f"[PROCESS] Traitement de l'offre {new_id} ({idx}/{len(new_ids)})...")
            
            # Récupération des détails
            offer_details = get_offer_details(new_id)
            
            if offer_details:
                # Envoi de la notification Discord
                if send_discord_notification(offer_details):
                    success_count += 1
                    
                # Delai entre chaque notification pour eviter le rate limit Discord
                # Discord limite a ~5 requetes par seconde pour les webhooks
                if idx < len(new_ids):  # Pas de delai apres la derniere
                    time.sleep(1.5)  # Attendre 1.5 secondes entre chaque notification
            else:
                log(f"[WARNING] Impossible de recuperer les details de l'offre {new_id}")
        
        # Sauvegarde des nouveaux IDs
        write_new_ids(IDS_FILE, new_ids)
        log(f"[SAVE] {len(new_ids)} ID(s) sauvegarde(s) dans {IDS_FILE}")
        log(f"[SUCCESS] {success_count}/{len(new_ids)} notification(s) envoyee(s) avec succes")
    else:
        log("[INFO] Aucune nouvelle offre trouvee")

else:
    log(f"[ERREUR] La requete API a echoue avec le code {response.status_code}")
    exit(1)

log("[DONE] Recherche terminee")
>>>>>>> Stashed changes
