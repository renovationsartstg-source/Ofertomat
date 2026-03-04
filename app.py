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
st.set_page_config(page_title="RenovationArt | Ofertomat PRO", page_icon="🏗️", layout="wide")

def get_base64(file_path):
    """Konwertuje obraz do Base64 dla bezpiecznego tła CSS."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

# Wybór tła: losujemy jedno z trzech zdjęć przy odświeżeniu
img_list = ["image1.png", "image2.png", "image3.png"]
active_imgs = [img for img in img_list if os.path.exists(img)]
selected_bg = random.choice(active_imgs) if active_imgs else None
bg_b64 = get_base64(selected_bg) if selected_bg else ""
logo_b64 = get_base64("logo.png")

# Wstrzyknięcie zaawansowanego CSS
style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    .stApp {{
        background-color: #F4F7F9;
    }}

    /* Ukrywanie elementów Streamlit */
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{ padding-top: 1rem !important; max-width: 1200px; }}

    /* BANER HERO (PANCERNY UKŁAD) */
    .hero-section {{
        background-image: linear-gradient(rgba(16, 43, 78, 0.8), rgba(16, 43, 78, 0.85)), 
                          url("data:image/png;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        padding: 50px 20px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 40px;
        border-bottom: 5px solid #D29A38;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }}

    .hero-logo {{
        max-width: 220px;
        height: auto;
        margin-bottom: 15px;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.4));
    }}

    .hero-subtitle {{
        color: #D29A38;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 1.2rem;
    }}

    /* KARTY METRYK */
    [data-testid="stMetric"] {{
        background-color: white;
        border-left: 6px solid #D29A38;
        border-radius: 12px;
        padding: 20px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }}
    
    [data-testid="stMetricValue"] {{
        color: #102B4E !important;
        font-weight: 700 !important;
    }}

    /* PRZYCISKI */
    .stButton > button {{
        background-color: #102B4E !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 25px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(16, 43, 78, 0.2);
    }}

    .stButton > button:hover {{
        background-color: #D29A38 !important;
        color: #102B4E !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(210, 154, 56, 0.4);
    }}

    /* ZAKŁADKI */
    .stTabs [data-baseweb="tab-list"] {{ gap: 12px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 30px;
        font-weight: 600;
        color: #5E6E85;
        border: 1px solid #E0E6ED;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #102B4E !important;
        color: #D29A38 !important;
        border: 1px solid #102B4E !important;
    }}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Wyświetlenie Banera
logo_tag = f'<img src="data:image/png;base64,{logo_b64}" class="hero-logo">' if logo_b64 else '<h1 style="color:white; margin:0;">RenovationArt</h1>'
st.markdown(f"""
    <div class="hero-section">
        {logo_tag}
        <div class="hero-subtitle">Profesjonalny System Ofertowania</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. BAZA DANYCH I LOGIKA SESJI
# ==========================================
DB_FILE = "baza_cen.csv"

@st.cache_data
def load_initial_data():
    return pd.DataFrame([
        {"Kategoria": "Malowanie", "Nazwa": "Malowanie 2-krotne (standard)", "Jm": "m2", "Robocizna": 25.0, "Material": 8.0},
        {"Kategoria": "Gładzie", "Nazwa": "Gładź gipsowa ze szlifowaniem", "Jm": "m2", "Robocizna": 60.0, "Material": 12.0},
        {"Kategoria": "Zabudowa G-K", "Nazwa": "Sufit podwieszany na stelażu", "Jm": "m2", "Robocizna": 160.0, "Material": 65.0},
        {"Kategoria": "Płytki", "Nazwa": "Układanie glazury (standard)", "Jm": "m2", "Robocizna": 160.0, "Material": 35.0},
        {"Kategoria": "Elektryka", "Nazwa": "Punkt elektryczny (kucie i kabel)", "Jm": "szt", "Robocizna": 120.0, "Material": 40.0}
    ])

if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.db = pd.read_csv(DB_FILE)
    else:
        st.session_state.db = load_initial_data()

if 'koszyk' not in st.session_state: st.session_state.koszyk = []
if 'klient' not in st.session_state: st.session_state.klient = {"nazwa": "", "adres": "", "data": datetime.date.today()}

# ==========================================
# 3. NAWIGACJA I PANEL BOCZNY
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Nawigacja")
    admin_active = st.query_params.get("admin") == "ukryte"
    tryb = st.radio("Wybierz widok:", ["📝 Kalkulator", "⚙️ Admin"] if admin_active else ["📝 Kalkulator"])
    
    st.markdown("---")
    if st.button("🗑️ Resetuj wycenę"):
        st.session_state.koszyk = []
        st.rerun()

# ==========================================
# WIDOK: KALKULATOR
# ==========================================
if tryb == "📝 Kalkulator":
    t1, t2, t3, t4 = st.tabs(["👤 Dane", "🛠️ Kreator", "💰 Kosztorys", "📊 Analiza"])

    with t1:
        st.markdown("#### Informacje o inwestycji")
        c1, c2 = st.columns(2)
        st.session_state.klient["nazwa"] = c1.text_input("Klient (Imię / Firma)", st.session_state.klient["nazwa"])
        st.session_state.klient["adres"] = c2.text_input("Adres realizacji", st.session_state.klient["adres"])

    with t2:
        st.markdown("#### Wybierz usługi")
        c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
        kat = c1.selectbox("Kategoria", st.session_state.db['Kategoria'].unique())
        uslugi_kat = st.session_state.db[st.session_state.db['Kategoria'] == kat]
        wybrana = c2.selectbox("Usługa", uslugi_kat['Nazwa'])
        ilosc = c3.number_input("Ilość", min_value=0.1, value=1.0)
        
        if c4.button("➕ Dodaj"):
            row = uslugi_kat[uslugi_kat['Nazwa'] == wybrana].iloc[0]
            st.session_state.koszyk.append({
                "Kategoria": row['Kategoria'], "Nazwa": row['Nazwa'], "Jm": row['Jm'], "Ilość": ilosc,
                "R_Suma": ilosc * row['Robocizna'], "M_Suma": ilosc * row['Material']
            })
            st.toast("Pozycja dodana!")

        if st.session_state.koszyk:
            st.dataframe(pd.DataFrame(st.session_state.koszyk), use_container_width=True, hide_index=True)

    with t3:
        if st.session_state.koszyk:
            df = pd.DataFrame(st.session_state.koszyk)
            c1, c2, c3 = st.columns(3)
            marza = c1.number_input("Marża (%)", value=10)
            rabat = c2.number_input("Rabat (%)", value=0)
            vat = c3.selectbox("VAT (%)", [8, 23, 0])

            suma_r = df['R_Suma'].sum()
            suma_m = df['M_Suma'].sum()
            suma_netto = (suma_r + suma_m) * (1 + marza/100) * (1 - rabat/100)
            kwota_vat = suma_netto * (vat/100)
            suma_brutto = suma_netto + kwota_vat

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Suma NETTO", f"{suma_netto:,.2f} zł")
            m2.metric(f"Podatek VAT ({vat}%)", f"{kwota_vat:,.2f} zł")
            m3.metric("DO ZAPŁATY (BRUTTO)", f"{suma_brutto:,.2f} zł")
            
            st.markdown("---")
            if st.button("📄 Pobierz Ofertę PDF (Wkrótce)"):
                st.info("Trwa generowanie dokumentu dla: " + st.session_state.klient["nazwa"])
        else:
            st.info("Dodaj usługi w zakładce Kreator.")

    with t4:
        if st.session_state.koszyk:
            totals = pd.DataFrame({
                "Typ": ["Robocizna", "Materiały"],
                "Wartość": [df['R_Suma'].sum(), df['M_Suma'].sum()]
            })
            fig = px.pie(totals, values='Wartość', names='Typ', hole=0.5, color_discrete_sequence=['#102B4E', '#D29A38'])
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# WIDOK: ADMIN
# ==========================================
elif tryb == "⚙️ Admin":
    st.header("🔐 Zarządzanie Cennikiem")
    if st.text_input("Hasło administratora", type="password") == "mateusz.rolo31":
        edytowany_df = st.data_editor(st.session_state.db, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Zapisz zmiany w bazie"):
            edytowany_df.to_csv(DB_FILE, index=False)
            st.session_state.db = edytowany_df
            st.success("Cennik zaktualizowany!")
