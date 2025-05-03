import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_ville_suggestions(query):
    """Appelle l'API Nominatim pour suggérer des villes selon la recherche."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "accept-language": "fr"
    }
    response = requests.get(url, params=params)
    return response.json()

def recherche_leboncoin(lat, lng, ville, prix_max, surface_min, pieces_min, rayon_km=20, nb_annonces=40):
    url = (
        f"https://www.leboncoin.fr/recherche?"
        f"category=9&real_estate_type=1&limit={nb_annonces}"
        f"&filters={{"
        f"\"enums\": {{\"real_estate_type\": [\"1\"]}},"
        f"\"ranges\": {{\"price\": {{\"max\": {prix_max}}}}},"
        f"\"location\": {{\"lat\": {lat}, \"lng\": {lng}, \"radius\": {rayon_km}}}"
        f"}}"
    )

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, "html.parser")

    annonces = []
    cards = soup.find_all("li", {"data-qa-id": "aditem_container"})
    for card in cards:
        titre = card.find("p", {"data-qa-id": "aditem_title"}).text.strip()
