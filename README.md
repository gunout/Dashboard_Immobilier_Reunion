# Dashboard_Immobilier_Reunion ( 24 Communes ) 2 METHODES ( HTTP ou LOCAL ) ( Données 2024 ) 
🏝️ Dashboard Immobilier Réunion  ℹ️ Données réelles DVF 2024 pour les communes (INSEE 97419), provenant de data.gouv.fr
<img width="662" height="465" alt="Screenshot_2025-10-15_18-46-48" src="https://github.com/user-attachments/assets/8c02bae0-9852-484e-8b1b-06b565a6517f" />

# EXAMPLE 

<img width="1280" height="1024" alt="Screenshot_2025-10-15_18-45-42" src="https://github.com/user-attachments/assets/98631cc0-e219-4903-a970-e72a2791917f" />
<img width="1280" height="1024" alt="Screenshot_2025-10-15_18-46-13" src="https://github.com/user-attachments/assets/f68d2cc1-59b6-4384-9a0c-114d0cb0f239" />
<img width="1280" height="1024" alt="Screenshot_2025-10-15_18-46-33" src="https://github.com/user-attachments/assets/0c16e5de-c6ff-4323-90ac-e34da13a623a" />

# INSTALL DEPENDENCIES 

    pip install beautifulsoup4 streamlit pandas requests plotly

# RUN DEPENDENCIES 

    streamlit run Dashboard.py

# METHODE LOCAL ( FICHIER LOCAL )

# TÉLÉCHARGEMENT " dvf_2024.csv " avec CURL

    curl -L -o dvf_2024.csv.gz "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/full.csv.gz"

# RUN PROGRAM ( PARIS - 20 Arrondissements ) METHODE LOCAL

    streamlit run Dash.py

PS : pour la methode local s'assurer d'avoir le fichier : dvf_2024.csv dans le meme dossier que Dash.py

By Gleaphe 2025 .
