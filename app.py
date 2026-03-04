import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. OPTYMALIZACJA WIZUALNA I DESIGN
# ==========================================
st.set_page_config(page_title="RenovationArt PRO", page_icon="🏗️", layout="wide")

@st.cache_data
def get_base64_cached(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: pass
    return ""

# Pobieranie zasobów
logo_b64 = get_base64_cached("logo.png")
tla_pliki = ["image1.png", "image2.png", "image3.png"]
aktywne = [t for t in tla_pliki if os.path.exists(t)]
wybrane_tlo = random.choice(aktywne) if aktywne else ""
bg_b64 = get_base64_cached(wybrane_tlo)

# STYLIZACJA CSS - "Glassmorphism" i Złoty Akcent
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.88), rgba(16, 43, 78, 0.95)), 
                    url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-attachment: fixed;
    }}

    h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stMetricLabel"] {{
        color: white !important;
        font-family: 'Montserrat', sans-serif !important;
    }}

    /* Pola wprowadzania danych */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: white !important;
        border: 1px solid rgba(210, 154, 56, 0.6) !important;
        border-radius: 8px !important;
    }}

    /* Złote Przyciski z Gradientem */
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important;
        color: #102B4E !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3.2rem !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s;
    }}
    .stButton > button:hover {{
        box-shadow: 0 8px 25px rgba(210, 154, 56, 0.5);
        transform: translateY(-2px);
    }}

    /* Karty Metryk i Tabele */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(210, 154, 56, 0.3) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        backdrop-filter: blur(10px);
    }}
    [data-testid="stMetricValue"] {{ color: #D29A38 !important; font-weight: 700 !important; }}

    .stDataFrame {{ background: rgba(255, 255, 255, 0.05) !important; border-radius: 10px; }}
    
    /* Ukrycie menu */
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/png;base64,{logo_b64}" style="max-width:240px; filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));"></div>', unsafe_allow_html=True)

# ==========================================
# 2. KOMPLEKSOWA BAZA USŁUG (11 KATEGORII)
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_base_data():
    return pd.DataFrame([
        # 1. WYBURZENIA I DEMONTAŻE
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Wyburzanie ścian (cegła/gazobeton)", "Jm": "m2", "R": 140.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż punktów hydraulicznych", "Jm": "szt", "R": 90.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Zbijanie tynków", "Jm": "m2", "R": 45.0, "M": 0.0},
        # 2. PRZYGOTOWANIE PODŁOŻA
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie powierzchni", "Jm": "m2", "R": 8.0, "M": 3.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 35.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Zabezpieczenie folią/taśmami", "Jm": "m2", "R": 10.0, "M": 5.0},
        # 3. ŚCIANY I SUFITY
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2x) + szlifowanie", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 30.0, "M": 12.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (białe)", "Jm": "m2", "R": 25.0, "M": 10.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż narożników aluminiowych", "Jm": "mb", "R": 25.0, "M": 6.0},
        # 4. ZABUDOWY G-K
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Sufit podwieszany na stelażu", "Jm": "m2", "R": 155.0, "M": 75.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Ścianka działowa z wygłuszeniem", "Jm": "m2", "R": 130.0, "M": 90.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Zabudowa stelaża podtynkowego WC", "Jm": "szt", "R": 450.0, "M": 180.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Wnęki oświetleniowe LED", "Jm": "mb", "R": 140.0, "M": 40.0},
        # 5. GLAZURA I TERAKOTA
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie płytek (60x60)", "Jm": "m2", "R": 170.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Szlifowanie narożników (45 stopni)", "Jm": "mb", "R": 150.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Hydroizolacja (systemowa)", "Jm": "m2", "R": 45.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie wielkiego formatu", "Jm": "m2", "R": 240.0, "M": 60.0},
        # 6. INSTALACJE ELEKTRYCZNE
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt elektryczny (kucie + puszka)", "Jm": "szt", "R": 130.0, "M": 50.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Biały montaż (gniazdko/włącznik)", "Jm": "szt", "R": 30.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż lampy/plafoniera", "Jm": "szt", "R": 80.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż taśmy LED w profilu", "Jm": "mb", "R": 60.0, "M": 40.0},
        # 7. INSTALACJE HYDRAULICZNE
        {"Kategoria": "07. Hydraulika", "Nazwa": "Podejście wodno-kanalizacyjne", "Jm": "szt", "R": 360.0, "M": 140.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż miski WC (wisząca)", "Jm": "szt", "R": 250.0, "M": 50.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż wanny/brodzika", "Jm": "szt", "R": 450.0, "M": 120.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż baterii podtynkowej", "Jm": "szt", "R": 350.0, "M": 80.0},
        # 8. PODŁOGI
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 45.0, "M": 15.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie winylu (klik)", "Jm": "m2", "R": 55.0, "M": 18.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż listew przypodłogowych", "Jm": "mb", "R": 35.0, "M": 10.0},
        # 9. STOLARKA I DRZWI
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż drzwi wewnętrznych", "Jm": "szt", "R": 280.0, "M": 40.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż parapetu wewnętrznego", "Jm": "mb", "R": 110.0, "M": 30.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Podcięcie drzwi", "Jm": "szt", "R": 50.0, "M": 0.0},
        # 10. OGRZEWANIE
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Pętla ogrzewania podłogowego", "Jm": "m2", "R": 60.0, "M": 55.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Montaż grzejnika", "Jm": "szt", "R": 220.0, "M": 60.0},
        # 11. SERWIS I PORZĄDKI
        {"Kategoria": "11. Serwis", "Nazwa": "Wywiezienie gruzu (kontener)", "Jm": "szt", "R": 100.0, "M": 650.0},
        {"Kategoria": "11. Serwis", "Nazwa": "Sprzątanie poeksploatacyjne", "Jm": "m2", "R": 20.0, "M": 10.0},
        {"Kategoria": "11. Serwis", "Nazwa": "Transport materiałów", "Jm": "godz", "R": 80.0, "M": 40.0}
    ])

if 'db' not in st.session_state:
    st.session_state.db = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else load_base_data()
if 'basket' not in st.session_state: st.session_state.basket = []

# ==========================================
# 3. INTERFEJS I LOGIKA SESJI
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ Panel Sterowania")
    admin = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok", ["Kalkulator", "Admin"] if admin else ["Kalkulator"])
    if st.button("🗑️ Nowa Wycena"):
        st.session_state.basket = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3, t4 = st.tabs(["👤 Klient", "🛠️ Kreator", "💰 Wynik", "📊 Analiza"])

    with t1:
        st.markdown("### Informacje Inwestora")
        name = st.text_input("Imię i Nazwisko / Firma", key="c_name")
        addr = st.text_input("Adres inwestycji", key="c_addr")

    with t2:
        st.markdown("### Konfiguracja Kosztorysu")
        c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
        
        kategorie = sorted(st.session_state.db['Kategoria'].unique())
        kat = c1.selectbox("Wybierz dział prac", kategorie)
        
        uslugi_kat = st.session_state.db[st.session_state.db['Kategoria'] == kat]
        usluga = c2.selectbox("Usługa", uslugi_kat['Nazwa'])
        
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0, step=1.0)
        
        if c4.button("➕ Dodaj"):
            row = uslugi_kat[uslugi_kat['Nazwa'] == usluga].iloc[0]
            st.session_state.basket.append({
                "Kategoria": row['Kategoria'], "Usługa": row['Nazwa'], "Ilość": ilosc, "Jm": row['Jm'],
                "R_Sum": ilosc * row['R'], "M_Sum": ilosc * row['M']
            })
            st.toast("Dodano do kosztorysu!")

        if st.session_state.basket:
            st.markdown("---")
            df_b = pd.DataFrame(st.session_state.basket)
            st.dataframe(df_b[["Usługa", "Ilość", "Jm", "R_Sum", "M_Sum"]], use_container_width=True)

    with t3:
        if st.session_state.basket:
            df = pd.DataFrame(st.session_state.basket)
            c1, c2, c3 = st.columns(3)
            marza = c1.slider("Marża firmy (%)", 0, 50, 15)
            rabat = c2.slider("Rabat (%)", 0, 20, 0)
            vat = c3.selectbox("VAT (%)", [8, 23, 0])

            baza = df['R_Sum'].sum() + df['M_Sum'].sum()
            netto = (baza * (1 + marza/100)) * (1 - rabat/100)
            brutto = netto * (1 + vat/100)

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Wartość NETTO", f"{netto:,.2f} zł")
            m2.metric("Podatek VAT", f"{(brutto-netto):,.2f} zł")
            m3.metric("DO ZAPŁATY", f"{brutto:,.2f} zł")
            
            if st.button("📄 Generuj Dokument PDF"):
                st.success(f"Oferta dla {name} gotowa.")
        else:
            st.info("Dodaj pierwsze pozycje w zakładce Kreator.")

    with t4:
        if st.session_state.basket:
            fig = px.pie(values=[df['R_Sum'].sum(), df['M_Sum'].sum()], 
                         names=['Robocizna', 'Materiały'], hole=0.5,
                         color_discrete_sequence=['#102B4E', '#D29A38'])
            st.plotly_chart(fig, use_container_width=True)

elif mode == "Admin":
    st.markdown("### 🔐 Zarządzanie Cennikiem")
    if st.text_input("Hasło", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz zmiany w bazie"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Baza zaktualizowana!")
