from fastapi import FastAPI
from fastapi.responses import FileResponse
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI()

# ✅ Configuration WebDriver (Chrome headless)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "API de Scraping en ligne 🚀"}

@app.get("/scrape")
def scrape_data():
    base_url = "https://www.bienici.com/recherche/achat/saint-quentin-02100?page="
    page_number = 1
    annonces_data = []

    while True:
        url = base_url + str(page_number)
        print(f"🔍 Scraping de la page {page_number} : {url}")

        driver.get(url)
        time.sleep(5)

        annonces = driver.find_elements(By.CSS_SELECTOR, "a.detailedSheetLink")
        if len(annonces) == 0:
            print(f"❌ Aucune annonce trouvée, fin du scraping.")
            break

        annonce_urls = [a.get_attribute("href") for a in annonces]
        print(f"✅ {len(annonce_urls)} annonces trouvées")

        for annonce_url in annonce_urls:
            driver.get(annonce_url)
            time.sleep(5)

            try:
                titre = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
                prix = driver.find_element(By.CSS_SELECTOR, ".ad-price__the-price").text.strip()
                description = driver.find_element(By.CSS_SELECTOR, ".see-more-description__content").text.strip()

                annonces_data.append({
                    "URL": annonce_url,
                    "Titre": titre,
                    "Prix": prix,
                    "Description": description
                })

            except Exception as e:
                print(f"❌ Erreur sur {annonce_url} : {e}")

        page_number += 1
        time.sleep(3)

    driver.quit()

    output_file = os.path.join(DATA_FOLDER, "scraping_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(annonces_data, f, indent=4, ensure_ascii=False)

    return {"message": "Scraping terminé!", "download_url": "/download"}

@app.get("/download")
def download_file():
    output_file = os.path.join(DATA_FOLDER, "scraping_result.json")
    if os.path.exists(output_file):
        return FileResponse(output_file, filename="scraping_result.json")
    return {"error": "Fichier introuvable"}

