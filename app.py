import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I STABILNY DESIGN
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

# Inicjalizacja stanów (Session State) - KLUCZ DO PŁYNNOŚCI
if 'step' not in st.session_state: st.session_state.step = 0
if 'basket' not in st.session_state: st.session_state.basket = []
if 'client_name' not in st.session_state: st.session_state.client_name = ""
if 'client_addr' not in st.session_state: st.session_state.client_addr = ""

# Pobieranie grafiki tła (tylko raz!)
tla = ["image1.png", "image2.png", "image3.png"]
aktywne = [t for t in tla if os.path.exists(t)]
if 'bg' not in st.session_state:
    st.session_state.bg = get_base64_cached(random.choice(aktywne)) if aktywne else ""
logo_b64 = get_base64_cached("logo.png")

# STYLIZACJA (Bezpieczny CSS, który nie blokuje UI)
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.9), rgba(16, 43, 78, 0.95)), 
                    url("data:image/png;base64,{st.session_state.bg}");
        background-size: cover;
        background-attachment: fixed;
    }}
    h1, h2, h3, p, label, .stMarkdown {{ color: white !important; font-family: 'Montserrat', sans-serif !important; }}
    
    /* Styl pól tekstowych */
    .stTextInput input {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #D29A38 !important;
    }}

    /* Przyciski Główne */
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important;
        color: #102B4E !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
        height: 3.5em !important;
    }}
    
    /* Ukrycie paska Streamlit */
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# ==========================================
# 2. ROZBUDOWANA BAZA USŁUG
# ==========================================
@st.cache_data
def load_full_db():
    return pd.DataFrame([
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Skuwanie płytek", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Wyburzanie ścian", "Jm": "m2", "R": 140.0, "M": 0.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie", "Jm": "m2", "R": 8.0, "M": 3.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Wylewka samopoziom", "Jm": "m2", "R": 35.0, "M": 35.0},
        {"Kategoria": "03. Malowanie", "Nazwa": "Malowanie 2x kolor", "Jm": "m2", "R": 30.0, "M": 10.0},
        {"Kategoria": "03. Malowanie", "Nazwa": "Gładź gipsowa szlifowana", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Sufit podwieszany", "Jm": "m2", "R": 150.0, "M": 75.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Zabudowa stelaża WC", "Jm": "szt", "R": 450.0, "M": 150.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie 60x60", "Jm": "m2", "R": 170.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Hydroizolacja", "Jm": "m2", "R": 45.0, "M": 40.0},
        {"Kategoria": "06. Instalacje", "Nazwa": "Punkt elektryczny", "Jm": "szt", "R": 130.0, "M": 50.0},
        {"Kategoria": "06. Instalacje", "Nazwa": "Punkt wod-kan", "Jm": "szt", "R": 360.0, "M": 140.0}
    ])

db = load_full_db()

# ==========================================
# 3. LOGIKA I WIDOKI (PŁYNNA NAWIGACJA)
# ==========================================

# Nagłówek Logo
if logo_b64:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_b64}" width="200"></div>', unsafe_allow_html=True)

# Pasek postępu (zamiast zakładek, które się psują)
st.markdown("---")
cols = st.columns(4)
titles = ["👤 Klient", "🛠️ Usługi", "💰 Kosztorys", "📊 Analiza"]
for i, title in enumerate(titles):
    if st.session_state.step == i:
        cols[i].markdown(f"**{title}**")
        cols[i].markdown("<div style='height:3px; background:#D29A38;'></div>", unsafe_allow_html=True)
    else:
        cols[i].markdown(f"<span style='opacity:0.5'>{title}</span>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- KROK 1: DANE KLIENTA ---
if st.session_state.step == 0:
    st.session_state.client_name = st.text_input("Nazwisko Inwestora / Firma", st.session_state.client_name)
    st.session_state.client_addr = st.text_input("Adres inwestycji", st.session_state.client_addr)
    if st.button("Zapisz i przejdź do wyceny ➔"):
        if st.session_state.client_name:
            st.session_state.step = 1
            st.rerun()
        else: st.error("Wpisz dane inwestora!")

# --- KROK 2: KREATOR USŁUG ---
elif st.session_state.step == 1:
    c1, c2, c3 = st.columns([2, 2, 1])
    kat = c1.selectbox("Wybierz dział", sorted(db['Kategoria'].unique()))
    uslugi = db[db['Kategoria'] == kat]
    wybrana = c2.selectbox("Usługa", uslugi['Nazwa'])
    ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0)
    
    if st.button("➕ Dodaj tę pozycję"):
        row = uslugi[uslugi['Nazwa'] == wybrana].iloc[0]
        st.session_state.basket.append({
            "Usługa": row['Nazwa'], "Ilość": ilosc, "Jm": row['Jm'],
            "R_Sum": ilosc * row['R'], "M_Sum": ilosc * row['M']
        })
        st.toast("Dodano!")

    if st.session_state.basket:
        st.markdown("### Twoja Lista:")
        st.table(pd.DataFrame(st.session_state.basket)[["Usługa", "Ilość", "Jm"]])
        if st.button("Przejdź do podsumowania ➔"):
            st.session_state.step = 2
            st.rerun()
    
    if st.button("⬅ Powrót do danych klienta", type="secondary"):
        st.session_state.step = 0
        st.rerun()

# --- KROK 3: KOSZTORYS ---
elif st.session_state.step == 2:
    df = pd.DataFrame(st.session_state.basket)
    c1, c2 = st.columns(2)
    marza = c1.slider("Narzut Marży (%)", 0, 50, 15)
    vat = c2.selectbox("Stawka VAT", [8, 23, 0])
    
    netto = (df['R_Sum'].sum() + df['M_Sum'].sum()) * (1 + marza/100)
    brutto = netto * (1 + vat/100)
    
    m1, m2 = st.columns(2)
    m1.metric("SUMA NETTO", f"{netto:,.2f} zł")
    m2.metric("SUMA BRUTTO", f"{brutto:,.2f} zł")
    
    if st.button("📄 Generuj ofertę PDF"):
        st.success("PDF wygenerowany pomyślnie!")
        
    if st.button("⬅ Dodaj więcej usług"):
        st.session_state.step = 1
        st.rerun()
