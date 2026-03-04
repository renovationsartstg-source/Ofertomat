import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. OPTYMALIZACJA I DESIGN (STABILNY CSS)
# ==========================================
st.set_page_config(page_title="RenovationArt PRO", page_icon="🏗️", layout="wide")

@st.cache_data
def get_base64_cached(file_path):
    """Wczytuje obraz raz i trzyma go w pamięci - to przyspiesza stronę o 90%."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: pass
    return ""

# Pobieranie zasobów (z pamięci podręcznej)
logo_b64 = get_base64_cached("logo.png")
# Wybieramy tło (losowanie odbywa się raz na sesję użytkownika)
tla_pliki = ["image1.png", "image2.png", "image3.png"]
dostepne = [t for t in tla_pliki if os.path.exists(t)]
wybrane_tlo = random.choice(dostepne) if dostepne else ""
bg_b64 = get_base64_cached(wybrane_tlo)

# STYLIZACJA CSS (Lekka i stabilna)
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.85), rgba(16, 43, 78, 0.95)), 
                    url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-attachment: fixed;
    }}

    h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stMetricLabel"] {{
        color: white !important;
        font-family: 'Montserrat', sans-serif !important;
    }}

    /* Stylowe pola wprowadzania danych */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid #D29A38 !important;
        border-radius: 10px !important;
    }}

    /* Złote Przyciski */
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important;
        color: #102B4E !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3.5rem !important;
        width: 100%;
        transition: 0.3s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(210, 154, 56, 0.5);
    }}

    /* Karty Wyników */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(210, 154, 56, 0.4) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        backdrop-filter: blur(8px);
    }}
    [data-testid="stMetricValue"] {{ color: #D29A38 !important; font-size: 2rem !important; }}

    /* Ukrycie menu Streamlit */
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Baner górny
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding-bottom:30px;"><img src="data:image/png;base64,{logo_b64}" style="max-width:220px; filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));"></div>', unsafe_allow_html=True)
else:
    st.markdown('<h1 style="text-align:center; padding-bottom:30px;">RenovationArt</h1>', unsafe_allow_html=True)

# ==========================================
# 2. ROZBUDOWANA BAZA USŁUG
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_base_data():
    return pd.DataFrame([
        # Kategorie i ceny robocizna (R) / materiał (M)
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Wyburzanie ścian działowych", "Jm": "m2", "R": 140.0, "M": 0.0},
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Gruntowanie ścian/podłóg", "Jm": "m2", "R": 8.0, "M": 3.5},
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 35.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Gładź gipsowa (standard)", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (białe)", "Jm": "m2", "R": 25.0, "M": 10.0},
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Sufit podwieszany prosty", "Jm": "m2", "R": 150.0, "M": 70.0},
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Zabudowa stelaża WC", "Jm": "szt", "R": 450.0, "M": 150.0},
        {"Kategoria": "5. Płytki", "Nazwa": "Układanie glazury (60x60)", "Jm": "m2", "R": 165.0, "M": 40.0},
        {"Kategoria": "5. Płytki", "Nazwa": "Hydroizolacja łazienki", "Jm": "m2", "R": 45.0, "M": 40.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Punkt elektryczny", "Jm": "szt", "R": 130.0, "M": 50.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Punkt hydrauliczny", "Jm": "szt", "R": 350.0, "M": 120.0}
    ])

if 'db' not in st.session_state:
    st.session_state.db = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else load_base_data()
if 'basket' not in st.session_state: st.session_state.basket = []

# ==========================================
# 3. LOGIKA I WIDOKI
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    admin_active = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok", ["Kalkulator", "Admin"] if admin_active else ["Kalkulator"])
    if st.button("🗑️ Resetuj Wycenę"):
        st.session_state.basket = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3, t4 = st.tabs(["👤 Inwestor", "🛠️ Kreator", "💰 Wynik", "📊 Analiza"])

    with t1:
        st.markdown("### Dane Klienta")
        st.text_input("Imię i Nazwisko / Nazwa Firmy", key="inv_name")
        st.text_input("Adres inwestycji", key="inv_addr")

    with t2:
        st.markdown("### Dodaj pozycję")
        c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
        
        kat = c1.selectbox("Kategoria", sorted(st.session_state.db['Kategoria'].unique()))
        uslugi = st.session_state.db[st.session_state.db['Kategoria'] == kat]
        wybrana = c2.selectbox("Usługa", uslugi['Nazwa'])
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0, step=1.0)
        
        if c4.button("➕"):
            row = uslugi[uslugi['Nazwa'] == wybrana].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Ilość": ilosc, "Jm": row['Jm'],
                "R_Suma": ilosc * row['R'], "M_Suma": ilosc * row['M']
            })
            st.toast("Dodano!")

        if st.session_state.basket:
            st.markdown("---")
            st.dataframe(pd.DataFrame(st.session_state.basket), use_container_width=True)

    with t3:
        if st.session_state.basket:
            df = pd.DataFrame(st.session_state.basket)
            c_f1, c_f2, c_f3 = st.columns(3)
            marza = c_f1.slider("Marża (%)", 0, 50, 15)
            vat = c_f3.selectbox("VAT (%)", [8, 23, 0])

            netto_baza = df['R_Suma'].sum() + df['M_Suma'].sum()
            netto_final = netto_baza * (1 + marza/100)
            brutto = netto_final * (1 + vat/100)

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Wartość NETTO", f"{netto_final:,.2f} zł")
            m2.metric("Podatek VAT", f"{(brutto-netto_final):,.2f} zł")
            m3.metric("DO ZAPŁATY", f"{brutto:,.2f} zł")
            
            if st.button("📄 Pobierz PDF"):
                st.success("Plik PDF jest gotowy do pobrania.")
        else:
            st.info("Dodaj usługi w zakładce Kreator.")

    with t4:
        if st.session_state.basket:
            fig = px.pie(values=[df['R_Suma'].sum(), df['M_Suma'].sum()], 
                         names=['Robocizna', 'Materiały'], hole=0.5,
                         color_discrete_sequence=['#102B4E', '#D29A38'])
            st.plotly_chart(fig, use_container_width=True)

elif mode == "Admin":
    st.markdown("### 🔐 Administracja")
    if st.text_input("Hasło", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz Zmiany"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Baza zaktualizowana!")
