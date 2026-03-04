import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I DESIGN (STABILNY CSS)
# ==========================================
st.set_page_config(page_title="RenovationArt | Oferty", page_icon="🏗️", layout="wide")

def get_base64_image(file_path):
    """Bezpieczne ładowanie obrazu do CSS."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# Ładowanie zasobów
logo_b64 = get_base64_image("logo.png")
tla = [img for img in ["image1.png", "image2.png", "image3.png"] if os.path.exists(img)]
wybrane_tlo = random.choice(tla) if tla else None
tlo_b64 = get_base64_image(wybrane_tlo) if wybrane_tlo else ""

# Wstrzykiwanie stylów
css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    .stApp {{
        background-color: #F8F9FB;
    }}

    /* Ukrywanie menu Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* PROFESJONALNY BANER GŁÓWNY */
    .hero-banner {{
        background-image: linear-gradient(rgba(16, 43, 78, 0.8), rgba(16, 43, 78, 0.8)), 
                          url("data:image/png;base64,{tlo_b64}");
        background-size: cover;
        background-position: center;
        padding: 50px 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 5px solid #D29A38;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}

    /* KONTROLA ROZMIARU LOGO */
    .main-logo {{
        max-width: 220px; /* ZMNIEJSZONE LOGO */
        height: auto;
        margin-bottom: 15px;
        filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.5));
    }}

    .hero-text {{
        color: #D29A38;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 1.2rem;
        margin-top: 10px;
    }}

    /* KARTY PODSUMOWANIA (Metryki) */
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 12px;
        padding: 20px !important;
        border-left: 6px solid #D29A38;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    
    [data-testid="stMetricValue"] {{
        color: #102B4E !important;
        font-weight: 700 !important;
    }}

    /* PRZYCISKI PREMIUM */
    div.stButton > button {{
        background-color: #102B4E !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        transition: 0.3s !important;
        width: 100%;
        box-shadow: 0 4px 10px rgba(16, 43, 78, 0.2);
    }}

    div.stButton > button:hover {{
        background-color: #D29A38 !important;
        color: #102B4E !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(210, 154, 56, 0.4);
    }}

    /* STYLIZACJA ZAKŁADEK */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 25px;
        font-weight: 600;
        border: 1px solid #E0E4E8;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #102B4E !important;
        color: #D29A38 !important;
        border: 1px solid #102B4E !important;
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Wyświetlanie banera (Logo + Tytuł)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="main-logo">' if logo_b64 else '<h1 style="color:white">RenovationArt</h1>'

st.markdown(f"""
    <div class="hero-banner">
        {logo_html}
        <div class="hero-text">Profesjonalny System Ofertowania</div>
    </div>
""", unsafe_allow_html=True)


# ==========================================
# 2. LOGIKA BAZY I SESJI
# ==========================================
DB_FILE = "baza_cen.csv"

def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Baza domyślna Pomorskie/Castorama
        d = [
            {"Kategoria": "Wykończenia", "Nazwa": "Gładź gipsowa + szlifowanie", "Jm": "m2", "Robocizna": 60.0, "Material": 12.0},
            {"Kategoria": "Wykończenia", "Nazwa": "Malowanie 2-krotne", "Jm": "m2", "Robocizna": 25.0, "Material": 8.0},
            {"Kategoria": "Zabudowy G-K", "Nazwa": "Sufit podwieszany prosty", "Jm": "m2", "Robocizna": 160.0, "Material": 65.0},
            {"Kategoria": "Płytki", "Nazwa": "Układanie glazury (standard)", "Jm": "m2", "Robocizna": 160.0, "Material": 35.0}
        ]
        df = pd.DataFrame(d)
        df.to_csv(DB_FILE, index=False)
        return df

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'items' not in st.session_state: st.session_state.items = []
if 'client' not in st.session_state: st.session_state.client = {"name": "", "address": ""}

# ==========================================
# 3. INTERFEJS
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Nawigacja")
    is_admin = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Menu:", ["Kalkulator", "Panel Admina"] if is_admin else ["Kalkulator"])
    if st.button("🗑️ Resetuj ofertę"):
        st.session_state.items = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3, t4 = st.tabs(["👤 Klient", "🛠️ Kreator", "💰 Kosztorys", "📊 Analiza"])

    with t1:
        st.session_state.client["name"] = st.text_input("Imię i Nazwisko / Firma", st.session_state.client["name"])
        st.session_state.client["address"] = st.text_input("Adres inwestycji", st.session_state.client["address"])

    with t2:
        st.markdown("#### Dodaj pozycję do wyceny")
        c1, c2, c3 = st.columns([2,2,1])
        kat = c1.selectbox("Wybierz kategorię", st.session_state.db['Kategoria'].unique())
        lista_uslug = st.session_state.db[st.session_state.db['Kategoria'] == kat]
        usluga = c2.selectbox("Wybierz usługę", lista_uslug['Nazwa'])
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0)
        
        if st.button("➕ Dodaj do listy"):
            row = lista_uslug[lista_uslug['Nazwa'] == usluga].iloc[0]
            st.session_state.items.append({
                "Nazwa": row['Nazwa'], "Ilość": ilosc, "Jm": row['Jm'],
                "R_Suma": ilosc * row['Robocizna'], "M_Suma": ilosc * row['Material']
            })
            st.toast("Pozycja dodana!")

        if st.session_state.items:
            st.dataframe(pd.DataFrame(st.session_state.items), use_container_width=True)

    with t3:
        if st.session_state.items:
            df_koszt = pd.DataFrame(st.session_state.items)
            c1, c2, c3 = st.columns(3)
            marza = c1.number_input("Marża (%)", value=10)
            rabat = c2.number_input("Rabat (%)", value=0)
            vat = c3.selectbox("VAT (%)", [8, 23, 0])

            suma_r = df_koszt['R_Suma'].sum()
            suma_m = df_koszt['M_Suma'].sum()
            suma_netto = (suma_r + suma_m) * (1 + marza/100) * (1 - rabat/100)
            kwota_vat = suma_netto * (vat/100)
            suma_brutto = suma_netto + kwota_vat

            m1, m2, m3 = st.columns(3)
            m1.metric("Suma Netto", f"{suma_netto:,.2f} zł")
            m2.metric("VAT", f"{kwota_vat:,.2f} zł")
            m3.metric("DO ZAPŁATY", f"{suma_brutto:,.2f} zł")

            if st.button("📄 Generuj PDF (Podgląd)"):
                st.info("Plik PDF zostanie wygenerowany z danymi klienta: " + st.session_state.client["name"])
        else:
            st.warning("Dodaj pozycje w kreatorze.")

    with t4:
        if st.session_state.items:
            fig_data = pd.DataFrame({
                "Typ": ["Robocizna", "Materiały"],
                "Wartość": [df_koszt['R_Suma'].sum(), df_koszt['M_Suma'].sum()]
            })
            fig = px.pie(fig_data, values='Wartość', names='Typ', hole=0.5, color_discrete_sequence=['#102B4E', '#D29A38'])
            st.plotly_chart(fig, use_container_width=True)

elif mode == "Panel Admina":
    st.header("🔐 Zarządzanie Cennikiem")
    haslo = st.text_input("Hasło:", type="password")
    if haslo == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Zapisz zmiany"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Cennik zaktualizowany!")
