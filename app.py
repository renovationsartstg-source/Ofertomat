import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I STYLIZACJA (CSS)
# ==========================================
st.set_page_config(page_title="RenovationArt | Ofertomat", page_icon="🏗️", layout="wide")

def get_base64(file_path):
    """Konwertuje obraz do Base64 dla bezpiecznego tła CSS."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return None

# Losowanie tła
img_list = ["image1.png", "image2.png", "image3.png"]
active_imgs = [img for img in img_list if os.path.exists(img)]
bg_b64 = get_base64(random.choice(active_imgs)) if active_imgs else ""
logo_b64 = get_base64("logo.png")

# Tło banera - jeśli brak obrazka, używamy samego koloru
banner_bg = f'url("data:image/png;base64,{bg_b64}")' if bg_b64 else "none"

style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif !important; background-color: #F4F7F9; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{ padding-top: 2rem !important; max-width: 1200px; }}

    .main-header {{
        background-image: linear-gradient(rgba(16, 43, 78, 0.85), rgba(16, 43, 78, 0.85)), {banner_bg};
        background-size: cover; background-position: center;
        padding: 60px 20px; border-radius: 15px; text-align: center;
        color: white; margin-bottom: 30px; border-bottom: 5px solid #D29A38;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }}
    .header-logo {{ max-width: 220px; margin-bottom: 15px; filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.25)); }}
    .header-subtitle {{ color: #D29A38; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; font-size: 1.1rem; }}
    [data-testid="stMetric"] {{ background-color: white; border-left: 6px solid #D29A38; border-radius: 10px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .stButton > button {{ background-color: #102B4E !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; width: 100%; transition: 0.3s !important; }}
    .stButton > button:hover {{ background-color: #D29A38 !important; color: #102B4E !important; transform: translateY(-2px); }}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Baner
logo_tag = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo">' if logo_b64 else '<h1 style="color:white">RenovationArt</h1>'
st.markdown(f'<div class="main-header">{logo_tag}<div class="header-subtitle">Profesjonalny System Ofertowania</div></div>', unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA I INTERFEJS
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_initial_data():
    return pd.DataFrame([
        {"Kategoria": "Malowanie", "Nazwa": "Malowanie 2x", "Jm": "m2", "Robocizna": 25.0, "Material": 4.0},
        {"Kategoria": "Płytki", "Nazwa": "Układanie glazury", "Jm": "m2", "Robocizna": 150.0, "Material": 25.0}
    ])

if 'db' not in st.session_state:
    if os.path.exists(DB_FILE): st.session_state.db = pd.read_csv(DB_FILE)
    else: st.session_state.db = load_initial_data()

if 'koszyk' not in st.session_state: st.session_state.koszyk = []

# Menu boczne
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    admin_mode = st.query_params.get("admin") == "ukryte"
    menu = st.radio("Widok:", ["Kalkulator", "Panel Admina"] if admin_mode else ["Kalkulator"])
    if st.button("🗑️ Resetuj ofertę"): 
        st.session_state.koszyk = []
        st.rerun()

# Kalkulator
if menu == "Kalkulator":
    t1, t2, t3 = st.tabs(["👤 Dane", "🛠️ Kreator", "💰 Podsumowanie"])
    with t1:
        st.text_input("Nazwa klienta")
        st.text_input("Adres")
    with t2:
        c1, c2, c3 = st.columns([2,2,1])
        kat = c1.selectbox("Kategoria", st.session_state.db['Kategoria'].unique())
        uslugi = st.session_state.db[st.session_state.db['Kategoria'] == kat]
        usluga = c2.selectbox("Usługa", uslugi['Nazwa'])
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0)
        if st.button("➕ Dodaj"):
            row = uslugi[uslugi['Nazwa'] == usluga].iloc[0]
            st.session_state.koszyk.append({"Nazwa": row['Nazwa'], "Suma": ilosc * (row['Robocizna'] + row['Material'])})
            st.toast("Dodano!")
    with t3:
        if st.session_state.koszyk:
            df = pd.DataFrame(st.session_state.koszyk)
            st.metric("RAZEM DO ZAPŁATY", f"{df['Suma'].sum():,.2f} zł")
        else:
            st.info("Koszyk jest pusty.")

# Admin
elif menu == "Panel Admina":
    st.header("Zarządzanie Cennikiem")
    if st.text_input("Hasło", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Zapisz"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Zapisano!")
