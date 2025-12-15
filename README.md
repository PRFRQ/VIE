# Détecteur de Nouvelles Offres de VIE

Ce script Python permet de détecter automatiquement la publication de nouvelles offres de VIE (Volontariat International en Entreprise) postées sur le site Business France [mon-vie-via.businessfrance.fr](https://mon-vie-via.businessfrance.fr/) et d'envoyer une notification enrichie via un Webhook Discord.

## ✨ Fonctionnalités

- **Détection automatique** : Interroge l'API de Business France pour détecter les nouvelles offres
- **Comparaison intelligente** : Compare les IDs des offres avec ceux présents dans `ids.txt`
- **Détails complets** : Récupère toutes les informations de l'offre (dates, salaire, localisation, télétravail, etc.)
- **Notifications Discord riches** : Envoie des embeds Discord formatés avec toutes les informations utiles
- **Logs détaillés** : Affichage de logs horodatés pour suivre l'exécution
- **Gestion d'erreurs robuste** : Gestion des timeouts, erreurs API, et champs manquants
- **Chemins relatifs** : Utilise le répertoire du script (plus besoin de chemins absolus)
- **Recherche LinkedIn** : Génère automatiquement un lien de recherche LinkedIn pour le contact

## 📋 Prérequis

- Python 3.6 ou supérieur
- Bibliothèque `requests` :
  ```bash
  pip install requests
  ```

## 🚀 Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/PRFRQ/VIE.git
   cd VIE
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez votre Webhook Discord dans le fichier `vie.py` (ligne 10) :
   ```python
   DISCORD_WEBHOOK_URL = "votre_webhook_discord_ici"
   ```

## ⚙️ Configuration

### Personnaliser la recherche

Modifiez le `payload` dans `vie.py` (ligne 153) pour personnaliser vos critères de recherche :

```python
payload = {
    "limit": 1000,                    # Nombre max d'offres à récupérer
    "skip": 0,                        # Pagination (offset)
    "latest": ["true"],               # Récupérer les dernières offres
    "query": "engineer",              # Mot-clé de recherche (null pour toutes)
    "missionsDurations": [],          # Durées spécifiques (vide = toutes)
    "geographicZones": ["2", "3"],   # Zones géographiques (continents)
    "activitySectorId": [],           # Secteurs d'activité
    "missionsTypesIds": [],           # Types de missions
    "countriesIds": [],               # Pays spécifiques
    "studiesLevelId": [],             # Niveaux d'études
    "companiesSizes": [],             # Tailles d'entreprises
    "specializationsIds": [],         # Spécialisations
    "entreprisesIds": [0],            # IDs d'entreprises
    "missionStartDate": None          # Date de début minimum
}
```

### Codes des zones géographiques

- `"2"` : Europe
- `"3"` : Asie
- `"4"` : Amérique du Nord
- `"5"` : Amérique du Sud
- `"6"` : Afrique
- `"8"` : Océanie


## 🔄 Comment ça marche ?

1. Le script interroge l'API `/api/Offers/search` avec les critères configurés
2. Il extrait les IDs des offres retournées
3. Il compare ces IDs avec ceux présents dans le fichier `ids.txt`
4. Pour chaque nouvelle offre détectée :
   - Interroge l'API `/api/Offers/details/{id}` pour obtenir tous les détails
   - Formate les données (dates, nom du contact, etc.)
   - Crée un embed Discord enrichi
   - Envoie la notification
   - Sauvegarde l'ID dans `ids.txt`

## 🖥️ Utilisation

### Exécution manuelle

```bash
python3 vie.py
```

### Exécution périodique (Linux/macOS)

Configurez un cron job pour une vérification automatique :

```bash
crontab -e
```

Exemples de configurations :
- **Toutes les 10 minutes** :
  ```
  */10 * * * * /usr/bin/python3 /chemin/vers/vie.py >> /chemin/vers/vie.log 2>&1
  ```
- **Toutes les heures** :
  ```
  0 * * * * /usr/bin/python3 /chemin/vers/vie.py >> /chemin/vers/vie.log 2>&1
  ```
- **Tous les jours à 9h** :
  ```
  0 9 * * * /usr/bin/python3 /chemin/vers/vie.py >> /chemin/vers/vie.log 2>&1
  ```

### Exécution périodique (Windows)

Utilisez le Planificateur de tâches Windows :
1. Ouvrez le Planificateur de tâches
2. Créez une nouvelle tâche
3. Configurez le déclencheur (ex: toutes les 10 minutes)
4. Action : Démarrer un programme → `python.exe` avec argument `/chemin/vers/vie.py`

## 📱 Configuration du Webhook Discord

1. Depuis un salon textuel Discord, accédez à ses paramètres
2. Rendez-vous dans l'onglet **Intégrations**
3. Cliquez sur **Webhooks** puis **Nouveau Webhook**

   ![Webhooks Discord](https://github.com/user-attachments/assets/8337ce8d-36bf-473e-b753-2f56bf5e9447)

4. Configurez le nom et l'icône du webhook
5. Copiez l'URL du webhook

   ![Copier URL](https://github.com/user-attachments/assets/c51b925b-8fb7-437d-9b8b-3727d21c04c7)

6. Collez l'URL dans le fichier `vie.py` à la ligne 10

## 📊 Exemple de notification

Chaque nouvelle offre génère une notification Discord contenant :
- 🏭 **Entreprise** : Nom de l'organisation
- 📅 **Durée** : Durée de la mission en mois
- ⚙️ **Secteur** : Secteur d'activité
- 🏙️ **Ville** : Ville d'affectation
- 🗺️ **Pays** : Pays de la mission
- 💵 **Indemnité** : Montant mensuel
- 🎬 **Début** : Date de début de mission
- 🏁 **Fin** : Date de fin de mission
- 📧 **Email** : Contact de l'entreprise
- 🌐 **Business France** : Lien vers l'offre complète
- 🔗 **LinkedIn** : Recherche automatique du contact
- 💼 **Télétravail** : Disponibilité du télétravail

## 🔧 Améliorations récentes

- ✅ Chemins de fichiers relatifs au script (plus portable)
- ✅ Logs horodatés avec emojis pour meilleure lisibilité
- ✅ Gestion robuste des erreurs et timeouts
- ✅ Gestion des champs null/manquants dans l'API
- ✅ Headers HTTP complets pour l'API
- ✅ Formatage amélioré des dates et montants
- ✅ Ajout du champ télétravail dans les notifications
- ✅ Statistiques de traitement (offres détectées, notifications envoyées)
- ✅ Code modulaire avec fonctions dédiées

## 📝 Structure du projet

```
VIE/
├── vie.py           # Script principal
├── ids.txt          # IDs des offres déjà traitées (auto-généré)
└── README.md        # Documentation
```

## 🐛 Dépannage

### Le script ne trouve aucune offre
- Vérifiez votre requête de recherche dans le `payload`
- Testez l'API manuellement avec un client REST (Postman, curl)

### Les notifications ne sont pas envoyées
- Vérifiez que l'URL du webhook Discord est correcte
- Assurez-vous que le webhook n'a pas été supprimé ou révoqué
- Consultez les logs pour voir les erreurs

### Erreurs de connexion
- Vérifiez votre connexion Internet
- L'API peut être temporairement indisponible

## 📜 Licence

Ce projet est open source et disponible sous licence MIT.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## ⚠️ Avertissement

Ce script utilise l'API publique de Business France. Veillez à respecter les conditions d'utilisation et à ne pas surcharger l'API avec des requêtes trop fréquentes.


 Dans le script  `vie.py` coller votre URL de webhook à la ligne 66 :  `discord_webhook_url `

![image](https://github.com/user-attachments/assets/e1cd81fe-af2b-435b-85e6-0bc9d5ec7a50)

5. Résultat
   
Vous recevrez ensuite ces notifications :

![image](https://github.com/user-attachments/assets/01d22451-51eb-412a-bec1-eab1cb0dbd98)



  
