import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64

# ==========================================
# 1. KONFIGURACJA STRONY I ANIMALOWANE TŁO (CSS/HTML)
# ==========================================
st.set_page_config(page_title="RenovationArt | System Wycen", page_icon="🏗️", layout="wide")

# Funkcja do wczytywania plików lokalnych i zamiany na Base64
def get_base64_of_image(file_name):
    try:
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                data = f.read()
            return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
    except Exception:
        pass
    return None

# Ładowanie 3 obrazów Base64 dla pokazu slajdów
image1_base64 = get_base64_of_image("image1.jpg") # Obrazek Tynkarza
image2_base64 = get_base64_of_image("image2.jpg") # Twoje Zdjęcie 1 (np. Salon)
image3_base64 = get_base64_of_image("image3.jpg") # Twoje Zdjęcie 2 (np. Łazienka)

# Przygotowanie kodów Base64 do wstawienia w HTML
images_base64 = []
for i, img in enumerate([image1_base64, image2_base64, image3_base64]):
    if img:
        images_base64.append(img)

# Jeśli nie wczytano żadnego obrazu, ustawiamy kolor jako awaryjny
if not images_base64:
    images_html_background = '<div class="fallback-background"></div>'
else:
    # Generujemy znaczniki HTML <img> dla każdego obrazu, z kodem Base64
    images_html_background = ""
    for i, img in enumerate(images_base64):
        images_html_background += f'<img src="{img}" class="slide active-{i+1}">'


# --- ZAAWANSOWANY CSS/HTML DLA PĘTLI OBRAZÓW W TLE ---
# Skomplikowany kod CSS obsługuje pętlę i przezroczystości (opacity)
advanced_design_css = """
<style>
    /* 1. Reset i Czcionka */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }

    /* 2. Baner z Animowanym Pokazem Slajdów w tle */
    .animated-banner {
        position: relative;
        padding: 60px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 40px;
        border-bottom: 6px solid #D29A38;
        box-shadow: 0 12px 24px rgba(16,43,78,0.25);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden; /* Krytyczne dla pętli w tle */
    }

    /* Nakładka Ciemna na obrazy (aby tekst był czytelny) */
    .overlay {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(16,43,78,0.7); /* Głęboki granat z 70% przezroczystością */
        z-index: 1; /* Pomiędzy obrazami a tekstem */
        border-radius: 12px;
    }

    /* Kontener dla Pętli Obrazów w tle */
    .animated-banner .slideshow {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: 0; /* Najniższa warstwa */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Stylizacja pojedynczych obrazów (Slajdów) w tle */
    .animated-banner .slide {
        position: absolute;
        width: 100%;
        height: 100%;
        object-fit: cover; /* Dopasowanie obrazu do kontenera */
        opacity: 0; /* Domyślnie niewidoczny */
        transition: opacity 1.5s ease-in-out; /* Płynne przechodzenie */
        border-radius: 12px;
    }

    /* Kluczowy kod CSS: Definiujemy animację i czas trwania dla pętli */
    /* Ustawiamy przezroczystość (opacity) w czasie, aby obrazy się przenikały */
    .animated-banner .slide { animation: slideAnimation 18s infinite; } /* Łącznie 18 sekund na 3 obrazy */
    
    /* Indywidualne opóźnienia dla przenikania */
    .active-1 { animation-delay: 0s; }
    .active-2 { animation-delay: 6s; } /* 18s / 3 obrazy = 6s na obraz */
    .active-3 { animation-delay: 12s; }

    /* Definicja animacji przenikania klatek */
    @keyframes slideAnimation {
        0%   { opacity: 0; }
        5%   { opacity: 1; }  /* Szybkie fade-in */
        25%  { opacity: 1; } /* Obraz widoczny (trzymanie) */
        33%  { opacity: 0; } /* Fade-out przed kolejnym */
        100% { opacity: 0; } /* Całkowicie niewidoczny do końca pętli */
    }

    /* Alternatywa, gdy nie ma obrazu */
    .fallback-background {
        position: absolute; top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(135deg, #102B4E 0%, #0a1b33 100%);
        z-index: 0; border-radius: 12px;
    }

    /* Treść na Banerze (Tekst) */
    .banner-text-content {
        position: relative;
        z-index: 2; /* Powyżej nakładki i obrazów */
    }
    
    .brand-title-text {
        color: #ffffff !important;
        font-size: 3.2rem !important;
        margin: 0 !important;
        font-weight: 700 !important;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: -15px !important; /* Zbliżenie tekstu */
    }
    
    .premium-banner p {
        color: #D29A38;
        margin: 15px 0 0 0;
        font-weight: 600;
        font-size: 1.3rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Reszta CSS z poprzedniego modułu (Metryki/Guziki) */
    [data-testid="stMetric"] { background-color: #ffffff; padding: 15px 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #f0f2f6; border-left: 5px solid #D29A38; }
    [data-testid="stMetricValue"] { color: #102B4E !important; font-weight: 700 !important; }
    .stButton > button { background-color: #102B4E !important; color: white !important; border-radius: 6px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { background-color: #D29A38 !important; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(210,154,56,0.3); }
</style>
"""
st.markdown(advanced_design_css, unsafe_allow_html=True)

# --- WYŚWIETLENIE ANIMOWANEGO BANERA ---
st.markdown(f"""
<div class="animated-banner">
    <div class="overlay"></div>
    <div class="slideshow">
        {images_html_background}
    </div>
    <div class="banner-text-content">
        <h1 class="brand-title-text">RenovationArt</h1>
        <p>Twoje Profesjonalne Ofertowanie</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 2. LOGIKA BAZY DANYCH I STANÓW
# ==========================================
DB_FILE = "baza_cen.csv"

def load_database():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Domyślna baza (Woj. Pomorskie 2026 + Castorama)
        data = [
            {"Kategoria": "Prace wyburzeniowe", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "Cena_Robocizna": 50.0, "Cena_Material": 0.0},
            {"Kategoria": "Malowanie i Gładzie", "Nazwa": "Gładź gipsowa (2-krotna + szlifowanie)", "Jm": "m2", "Cena_Robocizna": 60.0, "Cena_Material": 12.0},
            {"Kategoria": "Płytki", "Nazwa": "Układanie glazury (standard)", "Jm": "m2", "Cena_Robocizna": 150.0, "Cena_Material": 25.0},
            {"Kategoria": "Podłogi", "Nazwa": "Układanie paneli laminowanych/winylowych", "Jm": "m2", "Cena_Robocizna": 45.0, "Cena_Material": 15.0}
        ]
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False)
        return df

def init_session_state():
    if 'client_data' not in st.session_state:
        st.session_state.client_data = {"imie_nazwisko": "", "adres": "", "termin": datetime.date.today()}
    if 'pozycje_oferty' not in st.session_state:
        st.session_state.pozycje_oferty = []
    if 'financials' not in st.session_state:
        st.session_state.financials = {"marza_proc": 10.0, "rabat_proc": 0.0, "vat_proc": 8.0}
    if 'df_db' not in st.session_state:
        st.session_state.df_db = load_database()

init_session_state()

def calculate_totals():
    baza_robocizna = sum(item['Wartość_Robocizna'] for item in st.session_state.pozycje_oferty)
    baza_material = sum(item['Wartość_Materiał'] for item in st.session_state.pozycje_oferty)
    suma_bazowa = baza_robocizna + baza_material
    
    marza_kwota = suma_bazowa * (st.session_state.financials["marza_proc"] / 100)
    kwota_z_marza = suma_bazowa + marza_kwota
    
    rabat_kwota = kwota_z_marza * (st.session_state.financials["rabat_proc"] / 100)
    suma_netto = kwota_z_marza - rabat_kwota
    
    vat_kwota = suma_netto * (st.session_state.financials["vat_proc"] / 100)
    suma_brutto = suma_netto + vat_kwota
    
    return {
        "baza_robocizna": baza_robocizna, "baza_material": baza_material, "suma_bazowa": suma_bazowa,
        "marza_kwota": marza_kwota, "rabat_kwota": rabat_kwota, "suma_netto": suma_netto,
        "vat_kwota": vat_kwota, "suma_brutto": suma_brutto
    }

def normalize_text(text):
    replacements = {'ą':'a', 'ć':'c', 'ę':'e', 'ł':'l', 'ń':'n', 'ó':'o', 'ś':'s', 'ź':'z', 'ż':'z',
                    'Ą':'A', 'Ć':'C', 'Ę':'E', 'Ł':'L', 'Ń':'N', 'Ó':'O', 'Ś':'S', 'Ź':'Z', 'Ż':'Z'}
    for pl, asc in replacements.items():
        text = str(text).replace(pl, asc)
    return text

def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    totals = calculate_totals()
    client = st.session_state.client_data
    
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(0, 10, normalize_text("OFERTA CENOWA"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=10)
    pdf.cell(100, 6, normalize_text(f"Wykonawca: RenovationArt"), new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 6, normalize_text(f"Data: {datetime.date.today()}"), new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(10)
    
    # ... (RESZTA GENERATORA PDF BEZ ZMIAN) ...
    pdf.cell(100, 6, normalize_text(f"Klient: {client['imie_nazwisko']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    totals_pdf = calculate_totals()
    pdf.cell(100, 6, normalize_text(f"Suma do Zaplaty (Netto): {totals_pdf['suma_netto']:.2f} PLN"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 6, normalize_text(f"Suma do Zaplaty (Brutto): {totals_pdf['suma_brutto']:.2f} PLN"), new_x="LMARGIN", new_y="NEXT")
    
    return pdf.output()


# ==========================================
# 3. INTERFEJS UŻYTKOWNIKA (UI) I NAWIGACJA
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ Nawigacja")
    
    ukryty_panel_aktywny = st.query_params.get("admin") == "ukryte"
    if ukryty_panel_aktywny:
        tryb_aplikacji = st.radio("Zmień tryb:", ["📝 Kalkulator Ofert", "⚙️ Panel Administratora"])
    else:
        tryb_aplikacji = "📝 Kalkulator Ofert"
    
    st.markdown("---")
    if tryb_aplikacji == "📝 Kalkulator Ofert":
        if st.button("🗑️ Wyczyść kosztorys"):
            st.session_state.pozycje_oferty = []
            st.rerun()

# --- WIDOK 1: GŁÓWNA APLIKACJA ---
if tryb_aplikacji == "📝 Kalkulator Ofert":
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Dane Klienta", "🛠️ Kreator Usług", "💰 Wycena i PDF", "📊 Analiza"])

    with tab1:
        st.markdown("### Wprowadź informacje o kliencie")
        st.session_state.client_data["imie_nazwisko"] = st.text_input("Imię i Nazwisko", st.session_state.client_data["imie_nazwisko"])
        st.session_state.client_data["adres"] = st.text_input("Adres", st.session_state.client_data["adres"])

    with tab2:
        st.markdown("### Skomponuj zakres prac")
        with st.container():
            col_serv, col_qty, col_btn = st.columns([3, 1, 1])
            with col_serv:
                # Wczytujemy pełną listę z bazy sesji
                uslugi = st.session_state.df_db['Nazwa'].tolist()
                wybrana_usluga = st.selectbox("Wybierz usługę z bazy", uslugi)
            with col_qty:
                ilosc = st.number_input("Ilość", min_value=0.1, value=1.0)
            with col_btn:
                st.write("") 
                st.write("")
                if st.button("➕ Dodaj"):
                    row = st.session_state.df_db[st.session_state.df_db['Nazwa'] == wybrana_usluga].iloc[0]
                    nowa_pozycja = {
                        "Nazwa": row['Nazwa'], "Ilość": ilosc,
                        "Wartość_Robocizna": ilosc * row['Cena_Robocizna'],
                        "Wartość_Materiał": ilosc * row['Cena_Material']
                    }
                    st.session_state.pozycje_oferty.append(nowa_pozycja)
                    st.toast('Pozycja dodana!', icon='✅')

        if st.session_state.pozycje_oferty:
            st.dataframe(pd.DataFrame(st.session_state.pozycje_oferty), use_container_width=True)

    with tab3:
        st.markdown("### Finanse i generowanie oferty PDF")
        if st.session_state.pozycje_oferty:
            totals = calculate_totals()
            m1, m2 = st.columns(2)
            m1.metric("suma Netto", f"{totals['suma_netto']:.2f} zł")
            m2.metric("Suma Brutto", f"{totals['suma_brutto']:.2f} zł")
            
            if st.button("📄 Wygeneruj PDF"):
                pdf_bytes = generate_pdf()
                st.download_button("⬇️ Pobierz Ofertę", data=pdf_bytes, file_name="Oferta_RenovationArt.pdf", mime="application/pdf")

    with tab4:
        st.markdown("### Rentowność projektu")
        if st.session_state.pozycje_oferty:
            totals = calculate_totals()
            df_chart = pd.DataFrame({"Kategoria": ["Robocizna", "Materiały", "Marża"], "Wartość": [totals['baza_robocizna'], totals['baza_material'], totals['marza_kwota']]})
            fig = px.pie(df_chart, values='Wartość', names='Kategoria', hole=0.5)
            st.plotly_chart(fig, use_container_width=True)

# --- WIDOK 2: PANEL ADMINISTRATORA (ZABEZPIECZONY) ---
elif tryb_aplikacji == "⚙️ Panel Administratora":
    st.markdown("## 🔐 Zarządzanie Cennikiem")
    haslo = st.text_input("Hasło administratora:", type="password")
    
    if haslo == "mateusz.rolo31":
        st.data_editor(st.session_state.df_db, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz nowe ceny"):
             st.session_state.df_db.to_csv(DB_FILE, index=False)
             st.success("Baza zaktualizowana!")
