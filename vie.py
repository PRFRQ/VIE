#!/usr/bin/python3
import requests
import json
import re
#---------------FONCTIONS---------------
# Récupère les VIE déjà connus
def get_existing_ids(filename):
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()
# Sauvegarde les VIE connus
def write_new_ids(filename, ids):
    with open(filename, 'a') as f:
        for id in ids:
            f.write(f'{id}\n')

#---------------------------------------
# URL de l'API à interroger(Récupère les offres avec les options sélectionnés continent pays durée etc définit dans le payload)
api_url = "https://civiweb-api-prd.azurewebsites.net/api/Offers/search"

# limit = nbr d'offre, query = mot clé , missionsDurations = durrée VIE, gerographicZones = continent
payload = {
    "limit": 1000,
    "skip": 0,
    "query": "engineer",
    "missionsDurations": [],
    "gerographicZones": ["2", "3", "4", "6", "5", "8"],
    "activitySectorId": [],
    "missionsTypesIds": [],
    "countriesIds": [],
    "studiesLevelId": [],
    "companiesSizes": [],
    "specializationsIds": [],
    "entreprisesIds": [
        0
    ],
    "missionStartDate": None
}
# On convertit le payload en JSON pour transformer None en "null"
payload_json = json.dumps(payload)

# Envoie de la reqête
response = requests.post(api_url, data=payload_json, headers={'Content-Type': 'application/json'})

# Vérifiez si la requête a réussi
if response.status_code == 200:
    # Traitez les données (ici, nous les imprimons simplement)
    data = response.json()

    # Extrait les IDs
    ids = [item['id'] for item in data['result']]

    # On récupère les VIE que l'on connait déjà
    existing_ids = get_existing_ids('/home/stc/findVIE/ids.txt')
    
    # Trouvez les nouveaux IDs
    new_ids = [id for id in ids if str(id) not in existing_ids]
    
   # ...
    # Enregistre les nouveaux IDs dans un fichier
    write_new_ids('/home/stc/findVIE/ids.txt', new_ids)

    # URL du webhook Discord
    discord_webhook_url = "https://discord.com/api/webhooks/1240426483466375198/xXPGAy6CmJFg_-Nik5h3ZM7dEuQ_NKWMEDAECj-sGr6sjP-5P2mhE49_qotkwrlMC_SY"

    # Convertit la liste d'ID en string
    new_ids_str = ', '.join(str(id) for id in new_ids)
    new_ids_int = list(map(int, new_ids))

    for new_id in new_ids:
        # Convertit l'ID en string
        new_id_str = str(new_id)
        api_url = "https://civiweb-api-prd.azurewebsites.net/api/Offers/details/" + new_id_str
        response = requests.get(api_url)
        data = response.json()

        # Obtenez la date de début et de fin
        start_date = data['missionStartDate']
        end_date = data['missionEndDate']

        # Supprimez l'heure
        start_date = start_date.split('T')[0]
        end_date = end_date.split('T')[0]
        
        # Obtenez le nom du contact
        contact_name = data['contactName'].strip()

        # Remplacez les espaces par des '+'
        if contact_name.startswith("Madame "):
            contact_name = contact_name.replace("Madame ", "", 1)
        elif contact_name.startswith("Monsieur "):
            contact_name = contact_name.replace("Monsieur ", "", 1)
        contact_name = re.sub(r'^\s*', '', contact_name)
        contact_name_url = contact_name.replace(' ', '%20')

        # Ajoutez le nom du contact à l'URL LinkedIn
        linkedin_url = "https://www.linkedin.com/search/results/all/?keywords=" + contact_name_url
        businessFrance_url="https://mon-vie-via.businessfrance.fr/offres/"+new_id_str

        # Préparez le contenu de la notification
        content = {
            "embeds": [
                {
                    "title": data['missionTitle'],
                    "fields": [
                        {
                            "name": "🏭 Entreprise",
                            "value": data['organizationName'],
                            "inline": True
                        },
                        {
                            "name": "📅 Durée (mois)",
                            "value": str(data['missionDuration']),
                            "inline": True
                        },
                        {
                            "name": "⚙️ Secteur",
                            "value": data['activitySectorN1'],
                            "inline": True
                        },
                        {
                            "name": "🏙️ Ville",
                            "value": data['cityName'].strip(),
                            "inline": True
                        },
                        {
                            "name": "🗺️ Pays",
                            "value": data['countryName'],
                            "inline": True
                        },
                        {
                            "name": "💵 Salaire",
                            "value": str(data['indemnite']) + " €",
                            "inline": True
                        },
                        {
                            "name": "🎬 Début",
                            "value": start_date,
                            "inline": True
                        },
                        {
                            "name": "🏁 Fin",
                            "value": end_date,
                            "inline": True
                        },
                        {
                            "name": "📧 Email",
                            "value": data['contactEmail'],
                            "inline": True
                        },
                        {
                            "name": "🌐 Business France",
                            "value": "[Voir Offre]("+"{}".format(businessFrance_url)+")",
                            "inline": True
                        },
                        {
                            "name": "🌐 LinkedIn",
                            "value": "[Voir Profil Recruteur]("+("{}".format(linkedin_url))+")",
                            "inline": True
                        }
                    ],
                    "color": 16711680  # Couleur de la barre latérale (rouge dans cet exemple)
                }
            ]
        }
        
        # Envoyez la notification à Discord via le webhook
        requests.post(discord_webhook_url, data=json.dumps(content), headers={"Content-Type": "application/json"})

    else:
        print("Aucun nouvel ID trouvé.")
    
else:
    print("La requête API a échoué avec le code d'état", response.status_code)
