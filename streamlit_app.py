import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 🔍 Récupération des coordonnées via OpenStreetMap
def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json&limit=1"
    headers = {"User-Agent": "LeBonCoinApp"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lat']), float(data['lon'])
    return None, None

# 🧠 Fonction de scraping LeBonCoin
def recherche_leboncoin(ville, prix_max, surface_min, pieces_min, rayon_km=20, nb_annonces=40):
    lat, lng = get_coordinates(ville)
    if not lat or not lng:
        return None

    url = (
        f"https://www.leboncoin.fr/recherche?"
        f"category=9"
        f"&real_estate_type=1"
        f"&limit={nb_annonces}"
        f"&filters={{"
        f"\"enums\": {{\"real_estate_type\": [\"1\"]}},"
        f"\"ranges\": {{\"price\": {{\"max\": {prix_max}}}}},"
        f"\"location\": {{\"lat\": {lat}, \"lng\": {lng}, \"radius\": {rayon_km}}}"
        f"}}"
    )

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    annonces = []
    cards = soup.find_all("li", {"data-qa-id": "aditem_container"})
    for card in cards:
        titre = card.find("p", {"data-qa-id": "aditem_title"})
        prix = card.find("span", {"data-qa-id": "aditem_price"})
        localisation = card.find("p", {"data-qa-id": "aditem_location"})
        if titre and prix and localisation:
            annonces.append({
                "Titre": titre.text.strip(),
                "Prix": prix.text.strip(),
                "Localisation": localisation.text.strip()
            })
    return annonces

# 🖼️ Interface Streamlit
st.title("📍 Recherche d'annonces LeBonCoin")

ville = st.text_input("Ville", "Les Sables-d'Olonne")
prix_max = st.number_input("Prix maximum (€)", value=300000, step=10000)
surface_min = st.number_input("Surface minimale (m²)", value=40)
pieces_min = st.number_input("Nombre minimal de pièces", value=2)
rayon_km = st.slider("Rayon de recherche (km)", 5, 100, 20)

if st.button("Lancer la recherche"):
    annonces = recherche_leboncoin(ville, prix_max, surface_min, pieces_min, rayon_km)
    if annonces is None:
        st
