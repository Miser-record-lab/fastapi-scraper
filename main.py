from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import json
import time
import os

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 📌 Créer le dossier pour stocker les fichiers
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

app = FastAPI()

# 📌 Route de test pour voir si l'API fonctionne
@app.get("/")
def home():
    return {"message": "API de Scraping en ligne 🚀"}

# 📌 Fonction pour initialiser un WebDriver propre à chaque requête
def init_driver():
    """Initialise un WebDriver Chrome propre pour éviter les crashes."""
    chromedriver_autoinstaller.install()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Mode headless (pas d'interface graphique)
    chrome_options.add_argument("--no-sandbox")  # Nécessaire pour Railway
    chrome_options.add_argument("--disable-dev-shm-usage")  # Évite les erreurs mémoire
    chrome_options.add_argument("--disable-gpu")  # Désactive le GPU
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging

    return webdriver.Chrome(options=chrome_options)

# 📌 Route API pour scraper un site (Exemple avec Bienici)
@app.get("/scrape")
def scrape():
    """Scrape des annonces immobilières et retourne un fichier JSON."""
    base_url = "https://www.bienici.com/recherche/achat/saint-quentin-02100?page="
    page_number = 1
    annonces_data = []

    driver = init_driver()  # 🔥 Créer un WebDriver pour cette requête

    while True:
        url = base_url + str(page_number)
        print(f"\n🔍 Scraping de la page {page_number} : {url}")

        driver.get(url)
        time.sleep(5)  # Pause pour charger JS

        # ✅ Trouver les annonces
        annonces = driver.find_elements(By.CSS_SELECTOR, "a.detailedSheetLink")
        if len(annonces) == 0:
            print(f"❌ Aucune annonce trouvée sur la page {page_number}. Arrêt du scraping.")
            break

        # ✅ Extraire les URLs
        annonce_urls = [a.get_attribute("href") for a in annonces]
        print(f"✅ {len(annonce_urls)} annonces trouvées sur la page {page_number}")

        # 🔥 Scraper les détails de chaque annonce
        for annonce_url in annonce_urls:
            print(f"🔎 Scraping détails : {annonce_url}")
            driver.get(annonce_url)
            time.sleep(5)  # Pause pour charger la page

            try:
                titre = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
                prix = driver.find_element(By.CSS_SELECTOR, ".ad-price__the-price").text.strip()
                description = driver.find_element(By.CSS_SELECTOR, ".see-more-description__content").text.strip()

                # ✅ Ajouter les données
                annonces_data.append({
                    "URL": annonce_url,
                    "Titre": titre,
                    "Prix": prix,
                    "Description": description
                })

            except Exception as e:
                print(f"❌ Erreur sur {annonce_url} : {e}")

        # ✅ Passer à la page suivante
        page_number += 1
        time.sleep(3)

    driver.quit()  # 🔥 Fermer WebDriver après la requête

    # ✅ Sauvegarde en JSON
    output_file = f"{DATA_FOLDER}/bienici_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(annonces_data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Données enregistrées dans {output_file}")

    return FileResponse(output_file, media_type="application/json", filename="bienici_data.json")

