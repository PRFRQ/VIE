# Détecteur de Nouvelles Offres de VIE

Ce script Python permet de détecter la publication de nouvelles offres de VIE (Volontariat International en Entreprise) postées sur le site Business France [mon-vie-via.businessfrance.fr](https://mon-vie-via.businessfrance.fr/) et d'envoyer une notification via un Webhook Discord.

## Fonctionnalités

- **Détection de nouvelles offres** : Interroge l'API de Business France pour détecter les nouvelles offres.
- **Comparaison des IDs** : Compare les IDs des offres avec ceux présents dans un fichier `ids.txt`.
- **Détails des offres** : Récupère les détails des offres (date de début, date de fin, salaire, emplacement).
- **Notification Discord** : Envoie une notification via un Webhook Discord avec les détails des nouvelles offres.

## Comment ça marche ?

1. Le script interroge l'API [https://civiweb-api-prd.azurewebsites.net/api/Offers/search](https://civiweb-api-prd.azurewebsites.net/api/Offers/search) pour obtenir les offres actuelles.
2. Il compare les IDs des offres obtenues avec ceux présents dans le fichier `ids.txt`.
3. Si un ou plusieurs IDs ne sont pas présents dans le fichier, cela signifie que l'offre vient d'être publiée.
4. Le script interroge alors une deuxième API pour obtenir les détails (date de début, date de fin, salaire, emplacement) de l'offre publiée : [https://civiweb-api-prd.azurewebsites.net/api/Offers/details/ID_OFFRE](https://civiweb-api-prd.azurewebsites.net/api/Offers/details/ID_OFFRE).
5. Le Webhook Discord est ensuite construit avec tous ces détails.
6. L'ID de l'offre est ajouté au fichier `ids.txt`.
7. Le Webhook est ensuite envoyé via une requête POST.

## Configuration sur serveur Linux (Ubuntu server)

1. Clonez ce dépôt :
    ```
    git clone https://github.com/PRFRQ/VIE.git
    ```
2. Mettez en place une exécution périodique du script :
    ```
    crontab -l
    ```
    Par exemple pour une exécution toutes les 10 minutes ajoutez cette ligne :
   ```
    */10 * * * * /usr/bin/python3 /path/to/your/vie.py
    ```

4. Configurez votre Webhook Discord dans le fichier `vie.py`.
   
  Depuis un salon textuel Discord accèdez à ses paramètres et rendez vous dans l'onglet intégration puis cliquez sur Webhook
  
 ![image](https://github.com/user-attachments/assets/8337ce8d-36bf-473e-b753-2f56bf5e9447)
 
 Cliquez sur Nouveau Webhook
 
 ![image](https://github.com/user-attachments/assets/0977c9e3-9736-4765-9200-b256ea2ce788)

 Puis copiez l'URL du WebHook
 
 ![image](https://github.com/user-attachments/assets/c51b925b-8fb7-437d-9b8b-3727d21c04c7)

 Dans le script  `vie.py` coller votre URL de webhook à la ligne 66 :  `discord_webhook_url `

![image](https://github.com/user-attachments/assets/e1cd81fe-af2b-435b-85e6-0bc9d5ec7a50)

5. Résultat
   
Vous recevrez ensuite ces notifications :

![image](https://github.com/user-attachments/assets/01d22451-51eb-412a-bec1-eab1cb0dbd98)



  
