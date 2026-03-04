import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I WYDAJNY DESIGN (CSS)
# ==========================================
st.set_page_config(page_title="RenovationArt PRO", page_icon="🏗️", layout="wide")

@st.cache_data
def get_base64(file_path):
    """Wczytuje obraz raz i trzyma w pamięci - klucz do szybkości."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: pass
    return ""

# Pobieranie grafik (pamięć podręczna)
logo_b64 = get_base64("logo.png")
tla = ["image1.png", "image2.png", "image3.png"]
aktywne_tla = [t for t in tla if os.path.exists(t)]
wybrane_tlo = random.choice(aktywne_tla) if aktywne_tla else ""
bg_b64 = get_base64(wybrane_tlo)

# STYLIZACJA PREMIUM
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

    /* Pola wprowadzania (Inputy) */
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

# Logo
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding-bottom:30px;"><img src="data:image/png;base64,{logo_b64}" style="max-width:200px;"></div>', unsafe_allow_html=True)

# ==========================================
# 2. PEŁNA BAZA USŁUG (PRZYWRÓCONA)
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_base_data():
    return pd.DataFrame([
        # 1. WYBURZENIA
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Demontaż starej ościeżnicy", "Jm": "szt", "R": 80.0, "M": 0.0},
        {"Kategoria": "1. Wyburzenia", "Nazwa": "Wyburzanie ścian działowych (cegła)", "Jm": "m2", "R": 140.0, "M": 0.0},
        # 2. PRZYGOTOWANIE
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Gruntowanie ścian i sufitów", "Jm": "m2", "R": 8.0, "M": 3.5},
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 35.0},
        {"Kategoria": "2. Przygotowanie", "Nazwa": "Zabezpieczenie folią/taśmą", "Jm": "m2", "R": 10.0, "M": 5.0},
        # 3. GŁADZIE I MALOWANIE
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2-krotna) + szlifowanie", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (na biało)", "Jm": "m2", "R": 25.0, "M": 10.0},
        {"Kategoria": "3. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 30.0, "M": 12.0},
        # 4. ZABUDOWY G-K
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Sufit podwieszany prosty na stelażu", "Jm": "m2", "R": 150.0, "M": 75.0},
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Zabudowa stelaża WC", "Jm": "szt", "R": 450.0, "M": 150.0},
        {"Kategoria": "4. Zabudowy G-K", "Nazwa": "Ścianka działowa G-K", "Jm": "m2", "R": 120.0, "M": 85.0},
        # 5. PŁYTKI
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Układanie płytek (standard 60x60)", "Jm": "m2", "R": 165.0, "M": 45.0},
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Hydroizolacja (folia w płynie + taśmy)", "Jm": "m2", "R": 45.0, "M": 40.0},
        {"Kategoria": "5. Łazienka / Płytki", "Nazwa": "Szlifowanie narożników do kąta 45st.", "Jm": "mb", "R": 150.0, "M": 0.0},
        # 6. INSTALACJE
        {"Kategoria": "6. Instalacje", "Nazwa": "Punkt elektryczny (kucie+kabel+puszka)", "Jm": "szt", "R": 130.0, "M": 55.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Punkt hydrauliczny (podejście wod-kan)", "Jm": "szt", "R": 350.0, "M": 120.0},
        {"Kategoria": "6. Instalacje", "Nazwa": "Biały montaż (umywalka/WC/bateria)", "Jm": "szt", "R": 250.0, "M": 50.0},
        # 7. PODŁOGI
        {"Kategoria": "7. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 45.0, "M": 15.0},
        {"Kategoria": "7. Podłogi", "Nazwa": "Montaż listew przypodłogowych", "Jm": "mb", "R": 35.0, "M": 10.0}
    ])

if 'db' not in st.session_state:
    st.session_state.db = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else load_base_data()
if 'basket' not in st.session_state: st.session_state.basket = []

# ==========================================
# 3. INTERFEJS GŁÓWNY
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    admin_mode = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok:", ["Kalkulator", "Admin"] if admin_mode else ["Kalkulator"])
    if st.button("🗑️ Resetuj Wycenę"):
        st.session_state.basket = []
        st.rerun()

if mode == "Kalkulator":
    t1, t2, t3, t4 = st.tabs(["👤 Dane Inwestora", "🛠️ Kreator Usług", "💰 Podsumowanie", "📊 Analiza"])

    with t1:
        st.markdown("### Dane do oferty")
        name = st.text_input("Imię i Nazwisko / Firma", key="inv_name")
        addr = st.text_input("Adres realizacji", key="inv_addr")

    with t2:
        st.markdown("### Skomponuj zakres prac")
        c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
        
        kat_list = sorted(st.session_state.db['Kategoria'].unique())
        wybrana_kat = c1.selectbox("Kategoria", kat_list)
        
        uslugi_w_kat = st.session_state.db[st.session_state.db['Kategoria'] == wybrana_kat]
        wybrana_usluga = c2.selectbox("Usługa", uslugi_w_kat['Nazwa'])
        
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0, step=1.0)
        
        if c4.button("➕ Dodaj"):
            row = uslugi_w_kat[uslugi_w_kat['Nazwa'] == wybrana_usluga].iloc[0]
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
            c_f1, c_f2 = st.columns(2)
            marza = c_f1.slider("Marża firmy (%)", 0, 50, 15)
            vat = c_f2.selectbox("Stawka VAT (%)", [8, 23, 0])

            netto_baza = df['R_Suma'].sum() + df['M_Suma'].sum()
            netto_final = netto_baza * (1 + marza/100)
            brutto = netto_final * (1 + vat/100)

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Wartość NETTO", f"{netto_final:,.2f} zł")
            m2.metric("Podatek VAT", f"{(brutto-netto_final):,.2f} zł")
            m3.metric("DO ZAPŁATY", f"{brutto:,.2f} zł")
            
            if st.button("📄 Przygotuj plik PDF"):
                st.info(f"Dokument dla {name} zostanie wygenerowany.")
        else:
            st.info("Przejdź do 'Kreatora Usług', aby dodać pierwsze pozycje.")

    with t4:
        if st.session_state.basket:
            fig = px.pie(values=[df['R_Suma'].sum(), df['M_Suma'].sum()], 
                         names=['Robocizna', 'Materiały'], hole=0.5,
                         color_discrete_sequence=['#102B4E', '#D29A38'])
            st.plotly_chart(fig, use_container_width=True)

elif mode == "Admin":
    st.markdown("### 🔐 Administracja Cennikiem")
    if st.text_input("Hasło", type="password") == "mateusz.rolo31":
        new_db = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz Baze"):
            new_db.to_csv(DB_FILE, index=False)
            st.session_state.db = new_db
            st.success("Ceny zaktualizowane!")
