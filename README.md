# ia-leboncoin
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

# === Fonction de scraping LeBonCoin ===
def recherche_leboncoin(ville, prix_max, surface_min, pieces_min, rayon_km=20, nb_annonces=40):
    lat, lng = 46.4953, -1.7840  # Coordonnées approximatives des Sables-d'Olonne (à adapter dynamiquement si besoin)

    url = (
        f"https://www.leboncoin.fr/recherche"
        f"?category=9"
        f"&real_estate_type=1"
        f"&limit={nb_annonces}"
        f"&filters={{"
        f'    "enums": {{"real_estate_type": ["1"]}},'
        f'    "ranges": {{"price": {{"max": {prix_max}}}}},'
        f'    "location": {{"lat": {lat}, "lng": {lng}, "radius": {rayon_km}}}'
        f"}}"
    )

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.content, "html.parser")

    annonces = []
    cards = soup.find_all("li", {"data-qa-id": "aditem_container"})
    for card in cards:
        try:
            title = card.find("p", {"data-qa-id": "aditem_title"}).text.strip()
            price = card.find("span", {"data-qa-id": "aditem_price"}).text.strip()
            link = "https://www.leboncoin.fr" + card.find("a")["href"]
            infos = card.text.lower()

            surface = None
            pieces = None
            for mot in infos.split():
                if "m²" in mot:
                    try:
                        surface = int(mot.replace("m²", "").strip())
                    except:
                        pass
                if "pièce" in mot or "pièces" in mot:
                    try:
                        idx = infos.split().index(mot)
                        pieces = int(infos.split()[idx - 1])
                    except:
                        pass

            if surface and surface >= surface_min and (pieces is None or pieces >= pieces_min):
                annonces.append({
                    "Titre": title,
                    "Prix": price,
                    "Surface (m²)": surface,
                    "Pièces": pieces if pieces else "N/A",
                    "Lien": link
                })

        except:
            continue
    return annonces

# === Interface Streamlit ===
st.set_page_config(page_title="IA LeBonCoin", layout="centered")
st.title("🏡 IA de recherche LeBonCoin")
st.markdown("Automatisez votre veille immobilière en quelques clics.")

# === Formulaire ===
ville = st.text_input("Ville cible", "Les Sables-d'Olonne")
prix_max = st.number_input("Prix maximum (€)", value=300000)
surface_min = st.number_input("Surface minimale (m²)", value=40)
pieces_min = st.number_input("Nombre minimum de pièces", value=2)
rayon_km = st.slider("Rayon de recherche (km)", 5, 50, 20)

if st.button("🔍 Lancer la recherche"):
    with st.spinner("Recherche en cours..."):
        resultats = recherche_leboncoin(ville, prix_max, surface_min, pieces_min, rayon_km)

    if resultats:
        df = pd.DataFrame(resultats)
        st.success(f"{len(df)} biens trouvés")
        st.dataframe(df, use_container_width=True)

        # Préparer le téléchargement Excel
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Télécharger les résultats Excel",
            data=output.getvalue(),
            file_name="resultats_leboncoin.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Aucun bien trouvé avec ces critères.")
