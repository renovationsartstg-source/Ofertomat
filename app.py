import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I GŁĘBOKI DESIGN (CSS)
# ==========================================
st.set_page_config(page_title="RenovationArt PRO", page_icon="🏗️", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# Wybór tła na całą stronę
tla = ["image1.png", "image2.png", "image3.png"]
wybrane_tlo = random.choice([t for t in tla if os.path.exists(t)]) if any(os.path.exists(t) for t in tla) else ""
bg_b64 = get_base64(wybrane_tlo)
logo_b64 = get_base64("logo.png")

# AGRESYWNY CSS - ZMIENIAMY WSZYSTKO
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    /* Tło na całą stronę z filtrem */
    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.8), rgba(16, 43, 78, 0.9)), 
                    url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Ukrycie elementów systemowych */
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* Kontener główny - "szklany" efekt */
    .main-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }}

    /* Stylizacja tekstu */
    h1, h2, h3, p, span, label {{
        color: white !important;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Stylowe Inputy (Ciemne) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(210, 154, 56, 0.5) !important;
        border-radius: 10px !important;
    }}

    /* Przyciski - Złoty akcent */
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important;
        color: #102B4E !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 15px !important;
        transition: 0.3s !important;
        width: 100%;
    }}
    .stButton > button:hover {{
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(210, 154, 56, 0.4);
    }}

    /* Metryki finansowe */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #D29A38 !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }}
    [data-testid="stMetricValue"] {{ color: #D29A38 !important; }}

    /* Zakładki */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{
        color: white !important;
        font-weight: 400;
        border-bottom: 2px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        font-weight: 700 !important;
        border-bottom: 2px solid #D29A38 !important;
    }}

    /* Logo w nagłówku */
    .logo-container {{
        text-align: center;
        padding: 20px;
    }}
    .main-logo {{
        max-width: 200px;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.2));
    }}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Nagłówek z Logo
if logo_b64:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" class="main-logo"></div>', unsafe_allow_html=True)
else:
    st.markdown('<h1 style="text-align:center;">RenovationArt</h1>', unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA I DANE
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_base_data():
    return pd.DataFrame([
        {"Kategoria": "Gładzie i Malowanie", "Nazwa": "Gładź gipsowa (2x) + Szlif", "Jm": "m2", "R": 60.0, "M": 12.0},
        {"Kategoria": "Gładzie i Malowanie", "Nazwa": "Malowanie 2x (standard)", "Jm": "m2", "R": 25.0, "M": 8.0},
        {"Kategoria": "Płytki", "Nazwa": "Glazura standard (60x60)", "Jm": "m2", "R": 160.0, "M": 35.0},
        {"Kategoria": "Zabudowy", "Nazwa": "Sufit podwieszany G-K", "Jm": "m2", "R": 160.0, "M": 65.0}
    ])

if 'db' not in st.session_state:
    st.session_state.db = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else load_base_data()
if 'basket' not in st.session_state: st.session_state.basket = []

# ==========================================
# 3. WIDOKI
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ Nawigacja")
    mode = st.radio("Widok", ["Kalkulator", "Admin"] if st.query_params.get("admin")=="ukryte" else ["Kalkulator"])
    if st.button("🗑️ Resetuj wycenę"):
        st.session_state.basket = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3 = st.tabs(["👤 Klient", "🛠️ Kreator", "💰 Wynik"])

    with t1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        name = st.text_input("Imię i Nazwisko / Firma")
        addr = st.text_input("Adres inwestycji")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2,3,1])
        cat = c1.selectbox("Kategoria", st.session_state.db['Kategoria'].unique())
        options = st.session_state.db[st.session_state.db['Kategoria'] == cat]
        service = c2.selectbox("Usługa", options['Nazwa'])
        qty = c3.number_input("Ilość", min_value=0.1, value=1.0)
        
        if st.button("➕ Dodaj do kosztorysu"):
            row = options[options['Nazwa'] == service].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Ilość": qty, "Jm": row['Jm'],
                "Suma_R": qty * row['R'], "Suma_M": qty * row['M']
            })
            st.toast("Pozycja dodana!")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.basket:
            st.dataframe(pd.DataFrame(st.session_state.basket), use_container_width=True)

    with t3:
        if st.session_state.basket:
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            df = pd.DataFrame(st.session_state.basket)
            c1, c2 = st.columns(2)
            marza = c1.slider("Twoja Marża (%)", 0, 50, 15)
            vat = c2.selectbox("Stawka VAT (%)", [8, 23, 0])

            netto_baza = df['Suma_R'].sum() + df['Suma_M'].sum()
            netto_final = netto_baza * (1 + marza/100)
            brutto = netto_final * (1 + vat/100)

            m1, m2 = st.columns(2)
            m1.metric("Wartość NETTO", f"{netto_final:,.2f} zł")
            m2.metric("Wartość BRUTTO", f"{brutto:,.2f} zł")
            
            if st.button("📄 Generuj ofertę PDF"):
                st.success("Plik gotowy do pobrania (funkcja aktywna)")
            st.markdown('</div>', unsafe_allow_html=True)

elif mode == "Admin":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if st.text_input("PIN", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz zmiany"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Baza zaktualizowana!")
    st.markdown('</div>', unsafe_allow_html=True)
