import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA I DESIGN PREMIUM
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

# Inicjalizacja stanów sesji
if 'step' not in st.session_state: st.session_state.step = 0
if 'basket' not in st.session_state: st.session_state.basket = []
if 'client_name' not in st.session_state: st.session_state.client_name = ""
if 'client_addr' not in st.session_state: st.session_state.client_addr = ""
if 'margin' not in st.session_state: st.session_state.margin = 15.0
if 'discount' not in st.session_state: st.session_state.discount = 0.0

# Ładowanie tła
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

def create_pdf_bytes(name, addr, basket, netto, brutto, vat_val):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "OFERTA REMONTOWA - RenovationArt", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Inwestor: {normalize_pl(name)}", ln=True)
    pdf.cell(0, 8, f"Adres: {normalize_pl(addr)}", ln=True)
    pdf.cell(0, 8, f"Data: {datetime.date.today()}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 8, "Usluga", border=1); pdf.cell(25, 8, "Ilosc", border=1, align="C"); pdf.cell(20, 8, "Jm", border=1, align="C"); pdf.cell(55, 8, "Suma Netto", border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for item in basket:
        p_netto = (item['R_Sum'] + item['M_Sum']) * (1 + st.session_state.margin/100) * (1 - st.session_state.discount/100)
        pdf.cell(90, 7, normalize_pl(item['Usługa']), border=1)
        pdf.cell(25, 7, str(item['Ilość']), border=1, align="C")
        pdf.cell(20, 7, normalize_pl(item['Jm']), border=1, align="C")
        pdf.cell(55, 7, f"{p_netto:,.2f} zl", border=1, align="R")
        pdf.ln()
    pdf.ln(10); pdf.set_font("Helvetica", "B", 12)
    pdf.cell(140, 10, "SUMA NETTO:", align="R"); pdf.cell(50, 10, f"{netto:,.2f} zl", align="R", ln=True)
    pdf.cell(140, 10, f"PODATEK VAT ({vat_val}%):", align="R"); pdf.cell(50, 10, f"{(brutto-netto):,.2f} zl", align="R", ln=True)
    pdf.ln(2); pdf.set_font("Helvetica", "B", 14)
    pdf.cell(140, 12, "DO ZAPLATY (BRUTTO):", align="R"); pdf.cell(50, 12, f"{brutto:,.2f} zl", align="R", ln=True)
    
    # KLUCZOWA POPRAWKA: Konwersja bytearray na bytes
    return bytes(pdf.output())

# ==========================================
# 2. KOMPLEKSOWA BAZA USŁUG (12 KATEGORII)
# ==========================================
DB_FILE = "baza_cen.csv"
@st.cache_data
def load_db():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame([
        # 01. WYBURZENIA
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Wyburzanie ścian (cegła/gazobeton)", "Jm": "m2", "R": 145.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż drzwi i ościeżnic", "Jm": "szt", "R": 90.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Zbijanie tynków", "Jm": "m2", "R": 45.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż starej wanny/brodzika", "Jm": "szt", "R": 120.0, "M": 0.0},
        # 02. PRZYGOTOWANIE
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie powierzchni", "Jm": "m2", "R": 8.5, "M": 3.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 38.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Zabezpieczenie folią i taśmą", "Jm": "m2", "R": 12.0, "M": 6.0},
        # 03. ŚCIANY I SUFITY
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2x) + szlifowanie", "Jm": "m2", "R": 68.0, "M": 16.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 32.0, "M": 14.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (białe)", "Jm": "m2", "R": 26.0, "M": 10.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż narożników aluminiowych", "Jm": "mb", "R": 25.0, "M": 9.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Akrylowanie naroży", "Jm": "mb", "R": 10.0, "M": 4.5},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż fototapety/tapety", "Jm": "m2", "R": 60.0, "M": 10.0},
        # 04. ZABUDOWY G-K
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Sufit podwieszany na stelażu", "Jm": "m2", "R": 155.0, "M": 85.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Zabudowa stelaża podtynkowego WC", "Jm": "szt", "R": 480.0, "M": 190.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Ścianka działowa G-K z wygłuszeniem", "Jm": "m2", "R": 135.0, "M": 95.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Wnęka LED / Półka G-K", "Jm": "mb", "R": 160.0, "M": 55.0},
        # 05. PŁYTKI / GLAZURA
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie płytek standard (60x60)", "Jm": "m2", "R": 175.0, "M": 48.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Szlifowanie narożników 45st", "Jm": "mb", "R": 155.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Hydroizolacja łazienki (systemowa)", "Jm": "m2", "R": 45.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Cięcie otworów w gresie", "Jm": "szt", "R": 55.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Montaż odpływu liniowego", "Jm": "szt", "R": 420.0, "M": 110.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Cokół z płytek (cięcie+montaż)", "Jm": "mb", "R": 45.0, "M": 8.0},
        # 06. ELEKTRYKA
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt elektryczny (kucie+p)", "Jm": "szt", "R": 135.0, "M": 60.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Biały montaż (gniazdko/włącznik)", "Jm": "szt", "R": 32.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż lampy / kinkietu", "Jm": "szt", "R": 85.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż taśmy LED w profilu", "Jm": "mb", "R": 70.0, "M": 45.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt TV / Internet", "Jm": "szt", "R": 150.0, "M": 60.0},
        # 07. HYDRAULIKA
        {"Kategoria": "07. Hydraulika", "Nazwa": "Podejście wodno-kanalizacyjne", "Jm": "szt", "R": 380.0, "M": 150.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż miski WC / Bidetu", "Jm": "szt", "R": 260.0, "M": 60.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż wanny z obudową", "Jm": "szt", "R": 580.0, "M": 160.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż kabiny prysznicowej", "Jm": "szt", "R": 450.0, "M": 90.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż baterii podtynkowej", "Jm": "szt", "R": 360.0, "M": 85.0},
        # 08. PODŁOGI
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 48.0, "M": 15.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie winylu (klik)", "Jm": "m2", "R": 58.0, "M": 20.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż listew przypodłogowych", "Jm": "mb", "R": 38.0, "M": 12.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż progów/listew dylatacyjnych", "Jm": "szt", "R": 40.0, "M": 25.0},
        # 09. STOLARKA
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż drzwi wewnętrznych", "Jm": "szt", "R": 290.0, "M": 45.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż parapetu wewnętrznego", "Jm": "mb", "R": 125.0, "M": 35.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Podcięcie skrzydła drzwiowego", "Jm": "szt", "R": 60.0, "M": 0.0},
        # 10. OGRZEWANIE
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Pętle ogrzewania podłogowego", "Jm": "m2", "R": 68.0, "M": 65.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Montaż grzejnika łazienkowego", "Jm": "szt", "R": 260.0, "M": 75.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Przeniesienie punktu grzejnika", "Jm": "szt", "R": 350.0, "M": 120.0},
        # 11. DODATKI
        {"Kategoria": "11. Dodatki", "Nazwa": "Wklejenie lustra", "Jm": "m2", "R": 220.0, "M": 55.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Montaż karniszy", "Jm": "szt", "R": 75.0, "M": 0.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Montaż akcesoriów łazienkowych (uchwyty itp)", "Jm": "szt", "R": 45.0, "M": 0.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Silikonowanie brodzika/umywalki", "Jm": "szt", "R": 80.0, "M": 20.0},
        # 12. SERWIS / LOGISTYKA
        {"Kategoria": "12. Serwis", "Nazwa": "Kontener na gruz + utylizacja", "Jm": "szt", "R": 150.0, "M": 750.0},
        {"Kategoria": "12. Serwis", "Nazwa": "Sprzątanie końcowe obiektu", "Jm": "m2", "R": 25.0, "M": 10.0},
        {"Kategoria": "12. Serwis", "Nazwa": "Transport materiałów (roboczogodzina)", "Jm": "godz", "R": 85.0, "M": 0.0}
    ])

db_all = load_db()

# ==========================================
# 3. INTERFEJS I LOGIKA KROKÓW
# ==========================================
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/png;base64,{logo_b64}" width="220"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ Panel Sterowania")
    is_admin = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok:", ["Kalkulator", "🔒 Panel Admina"] if is_admin else ["Kalkulator"])
    if st.button("🗑️ Resetuj Wycenę"):
        st.session_state.step = 0; st.session_state.basket = []; st.rerun()

# --- PANEL ADMINA (Zarządzanie Marżą i Rabatem) ---
if mode == "🔒 Panel Admina":
    st.markdown("## 🔐 Ustawienia Prywatne")
    if st.text_input("Hasło dostępu", type="password") == "mateusz.rolo31":
        st.session_state.margin = st.slider("Marża firmy (%)", 0.0, 100.0, st.session_state.margin)
        st.session_state.discount = st.slider("Rabat dla klienta (%)", 0.0, 30.0, st.session_state.discount)
        new_db = st.data_editor(db_all, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz zmiany w bazie"):
            new_db.to_csv(DB_FILE, index=False); st.success("Zaktualizowano!")
    else: st.info("Podaj PIN.")

# --- KALKULATOR ---
elif mode == "Kalkulator":
    if st.session_state.step == 0:
        st.markdown("### 👤 Dane Inwestora")
        st.session_state.client_name = st.text_input("Imię i Nazwisko / Nazwa Firmy", st.session_state.client_name)
        st.session_state.client_addr = st.text_input("Adres inwestycji", st.session_state.client_addr)
        if st.button("Przejdź do wyceny ➔"):
            if st.session_state.client_name: st.session_state.step = 1; st.rerun()
            else: st.error("Wpisz dane inwestora.")

    elif st.session_state.step == 1:
        st.markdown("### 🛠️ Wybór prac")
        c1, c2, c3 = st.columns([2, 2, 1])
        kat = c1.selectbox("Dział prac", sorted(db_all['Kategoria'].unique()))
        opcje = db_all[db_all['Kategoria'] == kat]
        wybrana = c2.selectbox("Wybierz usługę", opcje['Nazwa'])
        unit = opcje[opcje['Nazwa']==wybrana]['Jm'].values[0]
        ilosc = c3.number_input(f"Ilość ({unit})", min_value=0.1, value=1.0)
        
        if st.button("➕ Dodaj do kosztorysu"):
            row = opcje[opcje['Nazwa'] == wybrana].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Ilość": ilosc, "Jm": row['Jm'],
                "R_Sum": ilosc * row['R'], "M_Sum": ilosc * row['M']
            })
            st.toast("Dodano!")

        if st.session_state.basket:
            st.markdown("---")
            st.dataframe(pd.DataFrame(st.session_state.basket)[["Usługa", "Ilość", "Jm"]], use_container_width=True)
            if st.button("Przejdź do podsumowania ➔"): st.session_state.step = 2; st.rerun()
        if st.button("⬅ Powrót do danych"): st.session_state.step = 0; st.rerun()

    elif st.session_state.step == 2:
        st.markdown("### 💰 Wynik Finansowy")
        df = pd.DataFrame(st.session_state.basket)
        vat = st.selectbox("Podatek VAT (%)", [8, 23, 0])
        
        sum_b = df['R_Sum'].sum() + df['M_Sum'].sum()
        # Przeliczenie z uwzględnieniem marży i rabatu z Panelu Admina
        netto = (sum_b * (1 + st.session_state.margin/100)) * (1 - st.session_state.discount/100)
        brutto = netto * (1 + vat/100)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("WARTOŚĆ NETTO", f"{netto:,.2f} zł")
        m2.metric("PODATEK VAT", f"{(brutto-netto):,.2f} zł")
        m3.metric("DO ZAPŁATY", f"{brutto:,.2f} zł")
        
        # --- POPRAWIONY GENERATOR PDF ---
        try:
            pdf_data = create_pdf_bytes(st.session_state.client_name, st.session_state.client_addr, st.session_state.basket, netto, brutto, vat)
            st.download_button(
                label="📄 POBIERZ OFERTĘ (PDF)",
                data=pdf_data,
                file_name=f"Oferta_{st.session_state.client_name.replace(' ','_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Błąd generatora: {e}")
        
        if st.button("⬅ Dodaj więcej usług"): st.session_state.step = 1; st.rerun()
