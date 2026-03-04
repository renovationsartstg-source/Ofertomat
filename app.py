import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I STYLIZACJA (PANCERNY CSS)
# ==========================================
st.set_page_config(page_title="RenovationArt PRO", page_icon="🏗️", layout="wide")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: pass
    return ""

# Wybór tła i logo
tla = ["image1.png", "image2.png", "image3.png"]
wybrane_tlo = random.choice([t for t in tla if os.path.exists(t)]) if any(os.path.exists(t) for t in tla) else ""
bg_b64 = get_base64(wybrane_tlo)
logo_b64 = get_base64("logo.png")

# STYLIZACJA - Łączymy design z funkcjonalnością
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    /* Tło całej aplikacji */
    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.8), rgba(16, 43, 78, 0.9)), 
                    url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Reset kolorów dla tekstów */
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: white !important;
        font-family: 'Montserrat', sans-serif;
    }}

    /* Naprawa widoczności pól tekstowych (Inputy) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #D29A38 !important;
        border-radius: 8px !important;
    }}
    
    /* Naprawa list rozwijanych (Selectbox options) */
    div[data-baseweb="popover"] {{
        background-color: #102B4E !important;
    }}

    /* Przyciski - Złoto */
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important;
        color: #102B4E !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 3em !important;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton > button:hover {{
        box-shadow: 0 0 15px rgba(210, 154, 56, 0.6);
        transform: translateY(-2px);
    }}

    /* Karty Metryk */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(210, 154, 56, 0.3) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        backdrop-filter: blur(5px);
    }}
    [data-testid="stMetricValue"] {{ color: #D29A38 !important; }}

    /* Tabela */
    .stDataFrame {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px;
    }}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Nagłówek
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/png;base64,{logo_b64}" style="max-width:200px;"></div>', unsafe_allow_html=True)
else:
    st.markdown('<h1 style="text-align:center;">RenovationArt</h1>', unsafe_allow_html=True)

# ==========================================
# 2. ROZBUDOWANA BAZA DANYCH
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_base_data():
    return pd.DataFrame([
        # PRACE WYBURZENIOWE
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Skuwanie starych płytek", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Demontaż punktów sanitarnych", "Jm": "szt", "R": 100.0, "M": 0.0},
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Wyburzanie ścian z cegły", "Jm": "m2", "R": 150.0, "M": 0.0},
        # PRACE PRZYGOTOWAWCZE
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Gruntowanie podłoży", "Jm": "m2", "R": 8.0, "M": 3.0},
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 30.0},
        # GŁADZIE I MALOWANIE
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2x) + szlifowanie", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (białe)", "Jm": "m2", "R": 25.0, "M": 8.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 30.0, "M": 10.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Montaż narożników aluminiowych", "Jm": "mb", "R": 25.0, "M": 5.0},
        # ZABUDOWY G-K
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Sufit podwieszany prosty", "Jm": "m2", "R": 140.0, "M": 65.0},
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Ścianka działowa G-K", "Jm": "m2", "R": 120.0, "M": 80.0},
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Zabudowa rur/stelaża WC", "Jm": "szt", "R": 450.0, "M": 120.0},
        # PŁYTKI
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Układanie płytek (standard 60x60)", "Jm": "m2", "R": 160.0, "M": 40.0},
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Układanie dekorów/mozaiki", "Jm": "mb", "R": 120.0, "M": 20.0},
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Hydroizolacja (folia w płynie)", "Jm": "m2", "R": 40.0, "M": 35.0},
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Szlifowanie narożników (45 stopni)", "Jm": "mb", "R": 150.0, "M": 0.0},
        # ELEKTRYKA I HYDRAULIKA
        {"Kategoria": "6. Instalacje", "Nazwa": "Punkt elektryczny (kucie+kabel)", "Jm": "szt", "R": 130.0, "M": 45.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Biały montaż elektryczny (gniazdka)", "Jm": "szt", "R": 30.0, "M": 0.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Punkt wodno-kanalizacyjny", "Jm": "szt", "R": 350.0, "M": 100.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Montaż miski WC / Umywalki", "Jm": "szt", "R": 250.0, "M": 50.0},
        # PODŁOGI
        {"Kategoria": "7. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 45.0, "M": 15.0},
        {"Kategoria": "7. Podłogi", "Nazwa": "Montaż listew przypodłogowych", "Jm": "mb", "R": 35.0, "M": 8.0}
    ])

if 'db' not in st.session_state:
    st.session_state.db = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else load_base_data()
if 'basket' not in st.session_state: st.session_state.basket = []

# ==========================================
# 3. INTERFEJS GŁÓWNY
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Nawigacja")
    mode = st.radio("Widok", ["Kalkulator", "Admin"] if st.query_params.get("admin")=="ukryte" else ["Kalkulator"])
    if st.button("🗑️ Resetuj wycenę"):
        st.session_state.basket = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3, t4 = st.tabs(["👤 Dane Klienta", "🛠️ Dodaj Usługi", "💰 Kosztorys", "📊 Analiza"])

    with t1:
        st.markdown("### Krok 1: Dane inwestora")
        name = st.text_input("Imię i Nazwisko / Firma", key="client_name")
        addr = st.text_input("Adres inwestycji", key="client_addr")

    with t2:
        st.markdown("### Krok 2: Wybór usług")
        c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
        
        # Filtracja kategorii i usług
        kategorie = sorted(st.session_state.db['Kategoria'].unique())
        wybrana_kat = c1.selectbox("Kategoria", kategorie)
        
        uslugi_w_kat = st.session_state.db[st.session_state.db['Kategoria'] == wybrana_kat]
        wybrana_usluga = c2.selectbox("Usługa", uslugi_w_kat['Nazwa'])
        
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0, step=1.0)
        
        if c4.button("➕ Dodaj"):
            row = uslugi_w_kat[uslugi_w_kat['Nazwa'] == wybrana_usluga].iloc[0]
            st.session_state.basket.append({
                "Kategoria": row['Kategoria'],
                "Usługa": row['Nazwa'],
                "Ilość": ilosc,
                "Jm": row['Jm'],
                "Robocizna": ilosc * row['R'],
                "Materiał": ilosc * row['M']
            })
            st.toast("Dodano do listy!")

        if st.session_state.basket:
            st.markdown("---")
            df_koszyk = pd.DataFrame(st.session_state.basket)
            st.dataframe(df_koszyk[["Usługa", "Ilość", "Jm", "Robocizna", "Materiał"]], use_container_width=True)

    with t3:
        if st.session_state.basket:
            st.markdown("### Krok 3: Finanse")
            df = pd.DataFrame(st.session_state.basket)
            
            c1, c2, c3 = st.columns(3)
            marza_proc = c1.slider("Marża firmy (%)", 0, 50, 15)
            rabat_proc = c2.slider("Rabat dla klienta (%)", 0, 20, 0)
            vat_proc = c3.selectbox("VAT (%)", [8, 23, 0])

            # Obliczenia
            baza_netto = df['Robocizna'].sum() + df['Materiał'].sum()
            z_marza = baza_netto * (1 + marza_proc/100)
            final_netto = z_marza * (1 - rabat_proc/100)
            kwota_vat = final_netto * (vat_proc/100)
            brutto = final_netto + kwota_vat

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Wartość NETTO", f"{final_netto:,.2f} zł")
            m2.metric("Podatek VAT", f"{kwota_vat:,.2f} zł")
            m3.metric("DO ZAPŁATY (BRUTTO)", f"{brutto:,.2f} zł")
            
            st.markdown("---")
            if st.button("📄 Pobierz PDF z Ofertą"):
                st.info(f"Generowanie oferty dla: {name}")
        else:
            st.warning("Dodaj pozycje w zakładce Kreator.")

    with t4:
        if st.session_state.basket:
            st.markdown("### Podział kosztów")
            df_chart = pd.DataFrame({
                "Typ": ["Robocizna", "Materiały"],
                "Wartość": [df['Robocizna'].sum(), df['Materiał'].sum()]
            })
            fig = px.pie(df_chart, values='Wartość', names='Typ', hole=0.5, 
                         color_discrete_sequence=['#102B4E', '#D29A38'])
            st.plotly_chart(fig, use_container_width=True)

elif mode == "Admin":
    st.markdown("### 🔐 Zarządzanie Cennikiem")
    if st.text_input("PIN Administratora", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz zmiany w bazie"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Cennik zaktualizowany!")
