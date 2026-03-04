import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I DESIGN (STABILNY)
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

# Inicjalizacja stanów sesji (Session State)
if 'step' not in st.session_state: st.session_state.step = 0
if 'basket' not in st.session_state: st.session_state.basket = []
if 'client_name' not in st.session_state: st.session_state.client_name = ""
if 'client_addr' not in st.session_state: st.session_state.client_addr = ""
# UKRYTE PARAMETRY FINANSOWE
if 'margin' not in st.session_state: st.session_state.margin = 15.0
if 'discount' not in st.session_state: st.session_state.discount = 0.0

# Grafiki
tla = ["image1.png", "image2.png", "image3.png"]
aktywne = [t for t in tla if os.path.exists(t)]
if 'bg' not in st.session_state:
    st.session_state.bg = get_base64_cached(random.choice(aktywne)) if aktywne else ""
logo_b64 = get_base64_cached("logo.png")

style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.9), rgba(16, 43, 78, 0.95)), 
                    url("data:image/png;base64,{st.session_state.bg}");
        background-size: cover; background-attachment: fixed;
    }}
    h1, h2, h3, p, label, .stMarkdown, [data-testid="stMetricLabel"] {{ color: white !important; font-family: 'Montserrat', sans-serif !important; }}
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.12) !important; color: white !important; border: 1px solid rgba(210, 154, 56, 0.5) !important; border-radius: 8px !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #D29A38 0%, #B0812D 100%) !important; color: #102B4E !important; font-weight: 700 !important; border: none !important; border-radius: 12px !important; width: 100%; height: 3.5em !important; text-transform: uppercase; transition: 0.3s ease;
    }}
    [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(210, 154, 56, 0.3) !important; border-radius: 15px !important; padding: 20px !important; backdrop-filter: blur(10px); }}
    [data-testid="stMetricValue"] {{ color: #D29A38 !important; }}
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
def normalize_pl(text):
    m = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
    for k, v in m.items(): text = str(text).replace(k, v)
    return text

def create_pdf(name, addr, basket, netto, brutto, vat_val):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "OFERTA REMONTOWA - RenovationArt", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Inwestor: {normalize_pl(name)}", ln=True)
    pdf.cell(0, 8, f"Adres: {normalize_pl(addr)}", ln=True)
    pdf.cell(0, 8, f"Data: {datetime.date.today()}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "Usluga", border=1)
    pdf.cell(30, 8, "Ilosc", border=1, align="C")
    pdf.cell(20, 8, "Jm", border=1, align="C")
    pdf.cell(40, 8, "Suma Netto", border=1, align="C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 9)
    for item in basket:
        # Przeliczamy netto pozycji uwzględniając marżę i rabat sesyjny
        pozycja_netto = (item['R_Sum'] + item['M_Sum']) * (1 + st.session_state.margin/100) * (1 - st.session_state.discount/100)
        pdf.cell(100, 7, normalize_pl(item['Usługa']), border=1)
        pdf.cell(30, 7, str(item['Ilość']), border=1, align="C")
        pdf.cell(20, 7, normalize_pl(item['Jm']), border=1, align="C")
        pdf.cell(40, 7, f"{pozycja_netto:,.2f} zl", border=1, align="R")
        pdf.ln()
        
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(150, 10, "SUMA NETTO:", align="R")
    pdf.cell(40, 10, f"{netto:,.2f} zl", align="R", ln=True)
    pdf.cell(150, 10, f"PODATEK VAT ({vat_val}%):", align="R")
    pdf.cell(40, 10, f"{(brutto-netto):,.2f} zl", align="R", ln=True)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(150, 12, "DO ZAPLATY (BRUTTO):", align="R")
    pdf.cell(40, 12, f"{brutto:,.2f} zl", align="R", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 2. BAZA DANYCH (11 KATEGORII)
# ==========================================
DB_FILE = "baza_cen.csv"
@st.cache_data
def load_db():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame([
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Wyburzanie ścian (cegła)", "Jm": "m2", "R": 140.0, "M": 0.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie powierzchni", "Jm": "m2", "R": 8.0, "M": 3.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 35.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2x) + szlifowanie", "Jm": "m2", "R": 65.0, "M": 15.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 30.0, "M": 12.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Sufit podwieszany na stelażu", "Jm": "m2", "R": 155.0, "M": 75.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Zabudowa stelaża WC", "Jm": "szt", "R": 450.0, "M": 180.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie płytek (standard 60x60)", "Jm": "m2", "R": 170.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Szlifowanie narożników 45st", "Jm": "mb", "R": 150.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt elektryczny (kucie+p)", "Jm": "szt", "R": 130.0, "M": 50.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Podejście wod-kan", "Jm": "szt", "R": 360.0, "M": 140.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 45.0, "M": 15.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż drzwi wewnętrznych", "Jm": "szt", "R": 280.0, "M": 40.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Pętle podłogówki", "Jm": "m2", "R": 60.0, "M": 55.0},
        {"Kategoria": "11. Serwis", "Nazwa": "Kontener na gruz", "Jm": "szt", "R": 100.0, "M": 650.0}
    ])

db_data = load_db()

# ==========================================
# 3. INTERFEJS I NAWIGACJA
# ==========================================
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/png;base64,{logo_b64}" width="200"></div>', unsafe_allow_html=True)

# Pasek Menu / Admin
with st.sidebar:
    st.markdown("### 🛠️ Opcje")
    admin_active = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok:", ["Kalkulator", "🔒 Panel Admina"] if admin_active else ["Kalkulator"])
    if st.button("🗑️ Resetuj Wycenę"):
        st.session_state.step = 0; st.session_state.basket = []; st.rerun()

# --- MODUŁ ADMINISTRATORA ---
if mode == "🔒 Panel Admina":
    st.markdown("## 🔐 Ustawienia Prywatne")
    if st.text_input("Hasło dostępu", type="password") == "mateusz.rolo31":
        st.markdown("### 1. Parametry Globalne Oferty")
        st.session_state.margin = st.slider("Twój Narzut / Marża (%)", 0.0, 100.0, st.session_state.margin)
        st.session_state.discount = st.slider("Rabat dla klienta (%)", 0.0, 30.0, st.session_state.discount)
        
        st.markdown("---")
        st.markdown("### 2. Edycja Cennika Usług")
        new_db = st.data_editor(db_data, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz zmiany w bazie"):
            new_db.to_csv(DB_FILE, index=False)
            st.success("Baza i parametry zaktualizowane!")
    else:
        st.info("Wpisz hasło, aby zarządzać marżą i cenami.")

# --- MODUŁ KALKULATORA ---
elif mode == "Kalkulator":
    # KROK 0: KLIENT
    if st.session_state.step == 0:
        st.markdown("### 👤 Dane Inwestora")
        st.session_state.client_name = st.text_input("Imię i Nazwisko", st.session_state.client_name)
        st.session_state.client_addr = st.text_input("Adres", st.session_state.client_addr)
        if st.button("Przejdź do wyceny ➔"):
            if st.session_state.client_name: st.session_state.step = 1; st.rerun()

    # KROK 1: USŁUGI
    elif st.session_state.step == 1:
        st.markdown("### 🛠️ Wybór prac")
        c1, c2, c3 = st.columns([2, 2, 1])
        kat = c1.selectbox("Dział", sorted(db_data['Kategoria'].unique()))
        opcje = db_data[db_data['Kategoria'] == kat]
        wybrana = c2.selectbox("Usługa", opcje['Nazwa'])
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0)
        
        if st.button("➕ Dodaj do listy"):
            row = opcje[opcje['Nazwa'] == wybrana].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Ilość": ilosc, "Jm": row['Jm'],
                "R_Sum": ilosc * row['R'], "M_Sum": ilosc * row['M']
            })
            st.toast("Dodano!")

        if st.session_state.basket:
            st.dataframe(pd.DataFrame(st.session_state.basket)[["Usługa", "Ilość", "Jm"]], use_container_width=True)
            if st.button("Przejdź do podsumowania ➔"): st.session_state.step = 2; st.rerun()

    # KROK 2: WYNIK
    elif st.session_state.step == 2:
        st.markdown("### 💰 Wynik Finansowy")
        df = pd.DataFrame(st.session_state.basket)
        vat_choice = st.selectbox("Stawka VAT (%)", [8, 23, 0])
        
        # Obliczenia na podstawie ukrytej marży i rabatu
        suma_baza = df['R_Sum'].sum() + df['M_Sum'].sum()
        netto = (suma_baza * (1 + st.session_state.margin/100)) * (1 - st.session_state.discount/100)
        brutto = netto * (1 + vat_choice/100)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("WARTOŚĆ NETTO", f"{netto:,.2f} zł")
        m2.metric("VAT", f"{(brutto-netto):,.2f} zł")
        m3.metric("DO ZAPŁATY (BRUTTO)", f"{brutto:,.2f} zł")
        
        # Generator PDF (używa parametrów z sesji)
        pdf_data = create_pdf(st.session_state.client_name, st.session_state.client_addr, st.session_state.basket, netto, brutto, vat_choice)
        st.download_button("📄 POBIERZ OFERTĘ (PDF)", data=pdf_data, file_name="Oferta_RenovationArt.pdf", mime="application/pdf")
        
        if st.button("⬅ Dodaj więcej usług"): st.session_state.step = 1; st.rerun()
