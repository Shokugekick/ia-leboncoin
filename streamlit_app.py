import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

def recherche_leboncoin(ville, prix_max, surface_min, pieces_min, rayon_km=20, nb_annonces=40):
    lat, lng = 46.4953, -1.7840  # Coordonnées des Sables-d'Olonne (modifiable dynamiquement si besoin)

    url = (
        f"https://www.leboncoin.fr/recherche?"
        f"category=9"
        f"&real_estate_type=1"
        f"&limit={nb_annonces}"
        f"&filters={{"
        f'  "enums": {{"real_estate_type": ["1"]}},'
        f'  "ranges": {{"price": {{"max": {prix_max}}}}},'
        f'  "location": {{"lat": {lat}, "lng": {lng}, "radius": {rayon_km}}}'
        f"}}"
    )

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, "html.parser")

    annonces = []
    cards = soup.find_all("li", {"data-qa-id": "aditem_container"})
    for card in cards:
        title = card.find("p", {"data-qa-id": "aditem_title"}).text if card.find("p", {"data-qa-id": "aditem_title"}) else ""
        price = card.find("span", {"data-qa-id": "aditem_price"}).text if card.find("span", {"data-qa-id": "aditem_price"}) else ""
        link = card.find("a")["href"] if card.find("a") else ""
        annonces.append({
            "Titre": title,
            "Prix": price,
            "Lien": f"https://www.leboncoin.fr{link}" if link.startswith("/") else link
        })

    return annonces

# --- Interface Streamlit ---
st.title("Recherche d'annonces LeBonCoin 📍")

ville = st.text_input("Ville", value="Les Sables-d'Olonne")
prix_max = st.number_input("Prix maximum (€)", value=300000, step=10000)
surface_min = st.number_input("Surface minimale (m²)", value=40, step=5)
pieces_min = st.number_input("Nombre minimal de pièces", value=2, step=1)
rayon_km = st.slider("Rayon de recherche (km)", 5, 100, 20)

if st.button("Lancer la recherche"):
    with st.spinner("Recherche en cours..."):
        annonces = recherche_leboncoin(ville, prix_max, surface_min, pieces_min, rayon_km)

    if annonces:
        df = pd.DataFrame(annonces)
        st.dataframe(df)

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button("📥 Télécharger les résultats (.xlsx)", data=buffer, file_name="annonces.xlsx", mime="application/vnd.ms-excel")
    else:
        st.warning("Aucune annonce trouvée.")
