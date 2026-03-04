import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import random

# ==========================================
# 1. KONFIGURACJA I PANCERNY, LEKKI DESIGN
# ==========================================
st.set_page_config(page_title="RenovationArt PRO", page_icon="🏗️", layout="wide")

# UWAGA: Podmień te linki na bezpośrednie linki do Twoich zdjęć na GitHubie 
# (format: https://raw.githubusercontent.com/TWOJA_NAZWA/TWOJE_REPO/main/image1.png)
# Na razie zostawiam puste/domyślne - aplikacja użyje eleganckiego gradientu jeśli nie znajdzie zdjęć.

tla_urls = [
    "https://images.unsplash.com/photo-1581094794329-c8112a89af12?q=80&w=2070&auto=format&fit=crop", # Przykładowe budowlane
    "https://images.unsplash.com/photo-1503387762-592dea58ef23?q=80&w=1932&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=2070&auto=format&fit=crop"
]
wybrane_tlo_url = random.choice(tla_urls)

# CSS wykorzystujący linki URL - to nie obciąża serwera ani przeglądarki
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.85), rgba(16, 43, 78, 0.95)), 
                    url("{wybrane_tlo_url}");
        background-size: cover;
        background-attachment: fixed;
    }}

    h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stMetricLabel"] {{
        color: white !important;
        font-family: 'Montserrat', sans-serif !important;
    }}

    /* Pola wprowadzania */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #D29A38 !important;
        border-radius: 8px !important;
    }}

    /* Przyciski Złote */
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important;
        color: #102B4E !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 3.2rem !important;
        transition: 0.3s;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(210, 154, 56, 0.4);
    }}

    /* Karty Metryk */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(210, 154, 56, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(5px);
    }}

    /* Ukrycie menu */
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Logo - Używamy st.image zamiast Base64 dla szybkości
col_l, col_m, col_r = st.columns([1,2,1])
with col_m:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=250)
    else:
        st.markdown("<h1 style='text-align:center;'>RenovationArt</h1>", unsafe_allow_html=True)

# ==========================================
# 2. BAZA DANYCH
# ==========================================
DB_FILE = "baza_cen.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame([
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Skuwanie płytek", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "2. Gładzie", "Nazwa": "Gładź gipsowa", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "3. Malowanie", "Nazwa": "Malowanie 2x", "Jm": "m2", "R": 25.0, "M": 10.0},
        {"Kategoria": "4. Płytki", "Nazwa": "Układanie 60x60", "Jm": "m2", "R": 165.0, "M": 40.0}
    ])

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'basket' not in st.session_state: st.session_state.basket = []

# ==========================================
# 3. INTERFEJS
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    admin = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok", ["Kalkulator", "Admin"] if admin else ["Kalkulator"])
    if st.button("🗑️ Reset"):
        st.session_state.basket = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3 = st.tabs(["👤 Klient", "🛠️ Kreator", "💰 Wynik"])

    with t1:
        st.text_input("Nazwa Klienta", key="c_name")
        st.text_input("Adres Inwestycji", key="c_addr")

    with t2:
        c1, c2, c3, c4 = st.columns([2,3,1,1])
        kat = c1.selectbox("Kategoria", sorted(st.session_state.db['Kategoria'].unique()))
        items = st.session_state.db[st.session_state.db['Kategoria'] == kat]
        serv = c2.selectbox("Usługa", items['Nazwa'])
        qty = c3.number_input("Ilość", min_value=0.1, value=1.0)
        
        if c4.button("➕"):
            row = items[items['Nazwa'] == serv].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Ilość": qty, "Jm": row['Jm'],
                "R_Suma": qty * row['R'], "M_Suma": qty * row['M']
            })
            st.toast("Dodano!")

        if st.session_state.basket:
            st.dataframe(pd.DataFrame(st.session_state.basket), use_container_width=True)

    with t3:
        if st.session_state.basket:
            df = pd.DataFrame(st.session_state.basket)
            marza = st.slider("Marża (%)", 0, 50, 15)
            
            suma_netto = (df['R_Suma'].sum() + df['M_Suma'].sum()) * (1 + marza/100)
            
            st.metric("DO ZAPŁATY (NETTO)", f"{suma_netto:,.2f} zł")
            if st.button("📄 Pobierz PDF"):
                st.info("Generowanie...")
        else:
            st.info("Dodaj usługi.")

elif mode == "Admin":
    if st.text_input("Hasło", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("OK!")
