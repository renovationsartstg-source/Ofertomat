import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ==========================================
# 1. KONFIGURACJA I DESIGN
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

if 'step' not in st.session_state: st.session_state.step = 0
if 'basket' not in st.session_state: st.session_state.basket = []
if 'client_name' not in st.session_state: st.session_state.client_name = ""
if 'client_addr' not in st.session_state: st.session_state.client_addr = ""
if 'margin' not in st.session_state: st.session_state.margin = 15.0
if 'discount' not in st.session_state: st.session_state.discount = 0.0
if 'inc_mat' not in st.session_state: st.session_state.inc_mat = True

tla = ["image1.png", "image2.png", "image3.png"]
aktywne = [t for t in tla if os.path.exists(t)]
if 'bg' not in st.session_state:
    st.session_state.bg = get_base64_cached(random.choice(aktywne)) if aktywne else ""
logo_b64 = get_base64_cached("logo.png")

style = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    .stApp {{
        background: linear-gradient(rgba(16, 43, 78, 0.92), rgba(16, 43, 78, 0.96)), 
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
    #MainMenu, footer, header {{visibility: hidden;}}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

def normalize_pl(text):
    m = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
    for k, v in m.items(): text = str(text).replace(k, v)
    return text

def send_email_silent(pdf_bytes, client_name):
    try:
        sender = st.secrets["email_user"]
        pwd = st.secrets["email_password"]
        msg = MIMEMultipart()
        msg['From'] = f"RenovationArt <{sender}>"
        msg['To'] = "renovationsartstg@gmail.com"
        msg['Subject'] = f"Kopia wyceny: {normalize_pl(client_name)}"
        msg.attach(MIMEText(f"Wygenerowano nową wycenę dla: {client_name}", 'plain'))
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= Oferta_{normalize_pl(client_name)}.pdf")
        msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)
        server.quit()
    except Exception:
        pass 

def create_pdf_bytes(name, addr, basket, netto, brutto, vat_val, include_mat):
    pdf = FPDF()
    pdf.add_page()
    navy, gold = (16, 43, 78), (210, 154, 56)
    
    if os.path.exists("logo.png"): pdf.image("logo.png", x=10, y=10, w=45)
    pdf.set_font("Helvetica", "B", 20); pdf.set_text_color(*navy)
    pdf.cell(0, 10, "OFERTA REMONTOWA", ln=True, align="R")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Data: {datetime.date.today()}", ln=True, align="R")
    pdf.ln(15); pdf.set_draw_color(*gold); pdf.set_line_width(1); pdf.line(10, 38, 200, 38); pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*navy)
    pdf.cell(95, 7, "ZLECENIODAWCA:", ln=False); pdf.cell(95, 7, "WYKONAWCA:", ln=True)
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(95, 6, normalize_pl(name), ln=False); pdf.cell(95, 6, "RenovationArt", ln=True)
    pdf.cell(95, 6, normalize_pl(addr), ln=False); pdf.cell(95, 6, "Starogard Gdanski", ln=True)
    pdf.cell(95, 6, "", ln=False); pdf.cell(95, 6, "Email: renovationsartstg@gmail.com", ln=True); pdf.ln(10)
    
    pdf.set_fill_color(*navy); pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 10, " Nazwa uslugi", fill=True); pdf.cell(20, 10, "Ilosc", fill=True, align="C"); pdf.cell(20, 10, "Jm", fill=True, align="C"); pdf.cell(55, 10, "Suma Netto ", fill=True, align="R"); pdf.ln()
    
    pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 9); fill = False; pdf.set_fill_color(245, 245, 245)
    for item in basket:
        m_cost = item['M_Sum'] if include_mat else 0
        p_netto = (item['R_Sum'] + m_cost) * (1 + st.session_state.margin/100) * (1 - st.session_state.discount/100)
        pdf.cell(95, 8, " " + normalize_pl(item['Usługa']), border='B', fill=fill); pdf.cell(20, 8, str(item['Ilość']), border='B', align="C", fill=fill); pdf.cell(20, 8, normalize_pl(item['Jm']), border='B', align="C", fill=fill); pdf.cell(55, 8, f"{p_netto:,.2f} zl ", border='B', align="R", fill=fill); pdf.ln(); fill = not fill
    
    pdf.ln(10); pdf.set_x(120); pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*navy)
    pdf.cell(40, 10, "SUMA NETTO:", ln=False); pdf.set_text_color(0, 0, 0); pdf.cell(40, 10, f"{netto:,.2f} zl", align="R", ln=True)
    pdf.set_x(120); pdf.set_text_color(*navy); pdf.cell(40, 10, f"VAT ({vat_val}%):", ln=False); pdf.set_text_color(0, 0, 0); pdf.cell(40, 10, f"{(brutto-netto):,.2f} zl", align="R", ln=True)
    pdf.set_draw_color(*gold); pdf.line(130, pdf.get_y(), 200, pdf.get_y()); pdf.set_x(120)
    pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(*gold); pdf.cell(40, 15, "DO ZAPLATY:", ln=False); pdf.cell(40, 15, f"{brutto:,.2f} zl", align="R", ln=True)
    
    return bytes(pdf.output())

# ==========================================
# 2. KOMPLETNA BAZA USŁUG (59 POZYCJI)
# ==========================================
DB_FILE = "baza_cen.csv"

def get_full_db():
    return pd.DataFrame([
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "R": 55.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Wyburzanie ścian (cegła/gazobeton)", "Jm": "m2", "R": 145.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż drzwi i ościeżnic", "Jm": "szt", "R": 90.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Zbijanie starych tynków", "Jm": "m2", "R": 45.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż starej wanny/brodzika", "Jm": "szt", "R": 120.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż paneli/podłóg drewnianych", "Jm": "m2", "R": 25.0, "M": 0.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie powierzchni", "Jm": "m2", "R": 8.5, "M": 3.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie szczepne (Betonkontakt)", "Jm": "m2", "R": 15.0, "M": 12.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 38.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Zabezpieczenie folią i taśmą", "Jm": "m2", "R": 12.0, "M": 6.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Naprawa pęknięć (siatka+gips)", "Jm": "mb", "R": 25.0, "M": 5.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Zabezpieczenie klatki schodowej/windy", "Jm": "szt", "R": 180.0, "M": 80.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2x) + szlifowanie", "Jm": "m2", "R": 68.0, "M": 16.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 32.0, "M": 14.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (białe)", "Jm": "m2", "R": 26.0, "M": 10.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż narożników aluminiowych", "Jm": "mb", "R": 25.0, "M": 9.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Akrylowanie naroży", "Jm": "mb", "R": 10.0, "M": 4.5},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż fototapety/tapety", "Jm": "m2", "R": 60.0, "M": 15.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż szyny sufitowej (karnisz ukryty)", "Jm": "mb", "R": 85.0, "M": 20.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Sufit podwieszany na stelażu", "Jm": "m2", "R": 155.0, "M": 85.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Zabudowa stelaża podtynkowego WC", "Jm": "szt", "R": 480.0, "M": 190.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Ścianka działowa G-K z wygłuszeniem", "Jm": "m2", "R": 135.0, "M": 95.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Wnęka LED / Półka G-K", "Jm": "mb", "R": 160.0, "M": 55.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Obróbka glifów drzwiowych/okiennych", "Jm": "mb", "R": 60.0, "M": 15.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie płytek standard (60x60)", "Jm": "m2", "R": 175.0, "M": 48.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie dużego formatu (120x60)", "Jm": "m2", "R": 220.0, "M": 60.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Szlifowanie narożników 45st (Jolly)", "Jm": "mb", "R": 155.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Montaż odpływu liniowego", "Jm": "szt", "R": 420.0, "M": 110.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Hydroizolacja łazienki (systemowa)", "Jm": "m2", "R": 45.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Cięcie otworów w gresie", "Jm": "szt", "R": 55.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Fugowanie epoksydowe", "Jm": "m2", "R": 40.0, "M": 30.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Silikonowanie (narożniki/brodzik)", "Jm": "mb", "R": 20.0, "M": 10.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt elektryczny (kucie+puszka)", "Jm": "szt", "R": 135.0, "M": 60.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Biały montaż (gniazdko/włącznik)", "Jm": "szt", "R": 32.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż osprzętu w płytkach (dodatek)", "Jm": "szt", "R": 25.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż lampy / kinkietu", "Jm": "szt", "R": 85.0, "M": 0.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Montaż taśmy LED w profilu", "Jm": "mb", "R": 70.0, "M": 45.0},
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt TV / Internet", "Jm": "szt", "R": 150.0, "M": 60.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Podejście wodno-kanalizacyjne", "Jm": "szt", "R": 380.0, "M": 150.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż miski WC / Bidetu", "Jm": "szt", "R": 260.0, "M": 60.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż wanny z obudową", "Jm": "szt", "R": 580.0, "M": 160.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż kabiny prysznicowej", "Jm": "szt", "R": 450.0, "M": 90.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż baterii podtynkowej", "Jm": "szt", "R": 360.0, "M": 85.0},
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż umywalki z szafką", "Jm": "szt", "R": 250.0, "M": 50.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 48.0, "M": 15.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie winylu (klik)", "Jm": "m2", "R": 58.0, "M": 20.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż listew przypodłogowych MDF", "Jm": "mb", "R": 38.0, "M": 12.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż listew progowych", "Jm": "szt", "R": 40.0, "M": 25.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż drzwi wewnętrznych standard", "Jm": "szt", "R": 290.0, "M": 45.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż drzwi ukrytych (Porta Hide)", "Jm": "szt", "R": 450.0, "M": 100.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż parapetu wewnętrznego", "Jm": "mb", "R": 125.0, "M": 35.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Podcięcie skrzydła drzwiowego", "Jm": "szt", "R": 60.0, "M": 0.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Pętle ogrzewania podłogowego", "Jm": "m2", "R": 68.0, "M": 65.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Montaż grzejnika łazienkowego", "Jm": "szt", "R": 260.0, "M": 75.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Wklejenie lustra", "Jm": "m2", "R": 220.0, "M": 55.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Montaż akcesoriów łazienkowych", "Jm": "szt", "R": 45.0, "M": 0.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Montaż karniszy", "Jm": "szt", "R": 75.0, "M": 20.0},
        {"Kategoria": "12. Serwis", "Nazwa": "Kontener na gruz + utylizacja", "Jm": "szt", "R": 150.0, "M": 750.0},
        {"Kategoria": "12. Serwis", "Nazwa": "Sprzątanie końcowe obiektu", "Jm": "m2", "R": 25.0, "M": 10.0}
    ])

@st.cache_data
def load_db():
    full_db = get_full_db()
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if len(df) < 50:
            full_db.to_csv(DB_FILE, index=False)
            return full_db
        return df
    else:
        full_db.to_csv(DB_FILE, index=False)
        return full_db

db_all = load_db()

# ==========================================
# 3. INTERFEJS UŻYTKOWNIKA I MENU
# ==========================================
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/png;base64,{logo_b64}" width="200"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ Menu Nawigacji")
    mode = st.radio("Zmień widok:", ["Kalkulator Wycen", "Panel Admina"])
    st.markdown("---")
    if st.button("🗑️ Resetuj Całą Wycenę"):
        st.session_state.step = 0
        st.session_state.basket = []
        st.rerun()

# --- BEZPOŚREDNI PANEL ADMINA ---
if mode == "Panel Admina":
    st.markdown("## 🔐 Logowanie do Panelu")
    pin = st.text_input("Wpisz kod PIN:", type="password")
    
    if pin == "mateusz.rolo31":
        st.success("Dostęp przyznany. Zarządzaj swoimi ustawieniami.")
        st.markdown("### Ustawienia Finansowe (Niewidoczne dla klienta)")
        
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            st.session_state.margin = st.slider("Twój Ukryty Narzut / Marża (%)", 0.0, 100.0, st.session_state.margin)
        with col_adm2:
            st.session_state.discount = st.slider("Rabat dla klienta (%)", 0.0, 30.0, st.session_state.discount)
        
        st.session_state.inc_mat = st.toggle("Domyślnie uwzględniaj materiał w wycenie", st.session_state.inc_mat)
        
        st.markdown("---")
        st.markdown("### Edytor Cennika i Usług")
        new_db = st.data_editor(db_all, num_rows="dynamic", use_container_width=True)
        col_save1, col_save2 = st.columns(2)
        
        with col_save1:
            if st.button("Zapisz zmiany w bazie cen"): 
                new_db.to_csv(DB_FILE, index=False)
                st.cache_data.clear()
                st.success("Baza została pomyślnie zaktualizowana!")
                st.rerun()
        
        with col_save2:
            # PRZYCISK RATUNKOWY
            if st.button("Twardy Reset Bazy (Wgraj 59 usług)"):
                default_db = get_full_db()
                default_db.to_csv(DB_FILE, index=False)
                st.cache_data.clear()
                st.success("Baza przywrócona do ustawień fabrycznych!")
                st.rerun()
                
    elif pin != "":
        st.error("Błędny PIN!")

# --- GŁÓWNY KALKULATOR ---
elif mode == "Kalkulator Wycen":
    # KROK 0: DANE KLIENTA
    if st.session_state.step == 0:
        with st.form("client_form"):
            st.markdown("### 👤 Krok 1: Dane Inwestora")
            c_name = st.text_input("Imię i Nazwisko / Nazwa Firmy", value=st.session_state.client_name)
            c_addr = st.text_input("Adres inwestycji (Opcjonalnie)", value=st.session_state.client_addr)
            if st.form_submit_button("Rozpocznij dodawanie usług ➔"):
                if c_name: 
                    st.session_state.client_name = c_name
                    st.session_state.client_addr = c_addr
                    st.session_state.step = 1
                    st.rerun()
                else: 
                    st.error("Proszę wpisać nazwę inwestora!")

    # KROK 1: DODAWANIE USŁUG
    elif st.session_state.step == 1:
        st.markdown("### 🛠️ Krok 2: Komponowanie Kosztorysu")
        c1, c2, c3 = st.columns([2, 2, 1])
        
        kat = c1.selectbox("Kategoria prac", sorted(db_all['Kategoria'].unique()))
        items = db_all[db_all['Kategoria'] == kat]
        serv = c2.selectbox("Konkretna usługa", items['Nazwa'])
        
        unit = items[items['Nazwa']==serv]['Jm'].values[0]
        qty = c3.number_input(f"Wymagana ilość ({unit})", min_value=0.1, value=1.0)
        
        if st.button("➕ Dodaj do listy"):
            row = items[items['Nazwa'] == serv].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Kategoria": row['Kategoria'], "Ilość": qty, "Jm": row['Jm'],
                "R_Sum": qty * row['R'], "M_Sum": qty * row['M']
            })
            st.toast(f"Dodano: {row['Nazwa']}")

        if st.session_state.basket:
            st.markdown("#### Twoja obecna lista:")
            st.dataframe(pd.DataFrame(st.session_state.basket)[["Usługa", "Ilość", "Jm"]], use_container_width=True)
            
            col1, col2 = st.columns(2)
            if col1.button("⬅ Wróć do edycji klienta"): 
                st.session_state.step = 0; st.rerun()
            if col2.button("Przejdź do podsumowania ➔"): 
                st.session_state.step = 2; st.rerun()
        else:
            if st.button("⬅ Wróć"): st.session_state.step = 0; st.rerun()

    # KROK 2: WYNIK I ANALIZA
    elif st.session_state.step == 2:
        df = pd.DataFrame(st.session_state.basket)
        st.markdown(f"### 💰 Krok 3: Ostateczny Kosztorys dla {st.session_state.client_name}")
        
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1: 
            inc_mat = st.toggle("Uwzględnij koszty materiałów w wycenie", value=st.session_state.inc_mat)
        with c_opt2: 
            vat = st.selectbox("Podatek VAT (%)", [8, 23, 0])
        
        sum_r = df['R_Sum'].sum()
        sum_m = df['M_Sum'].sum() if inc_mat else 0
        netto = (sum_r + sum_m) * (1 + st.session_state.margin/100) * (1 - st.session_state.discount/100)
        brutto = netto * (1 + vat/100)
        
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("WARTOŚĆ NETTO", f"{netto:,.2f} zł")
        m2.metric(f"PODATEK VAT ({vat}%)", f"{(brutto-netto):,.2f} zł")
        m3.metric("DO ZAPŁATY (BRUTTO)", f"{brutto:,.2f} zł")
        
        st.markdown("### 📊 Analiza Rentowności Projektu")
        ca1, ca2 = st.columns(2)
        with ca1: 
            st.plotly_chart(px.pie(values=[sum_r, sum_m] if inc_mat else [sum_r], names=['Robocizna', 'Materiały'] if inc_mat else ['Robocizna'], hole=0.4, title="Podział Kosztów Głównych", color_discrete_sequence=['#102B4E', '#D29A38']), use_container_width=True)
        with ca2: 
            df_c = df.copy()
            df_c['Total'] = df_c['R_Sum'] + (df_c['M_Sum'] if inc_mat else 0)
            st.plotly_chart(px.bar(df_c.groupby('Kategoria')['Total'].sum().reset_index(), x='Kategoria', y='Total', title="Koszty wg Kategorii Prac", color_discrete_sequence=['#D29A38']), use_container_width=True)

        st.markdown("---")
        
        pdf_bytes = create_pdf_bytes(st.session_state.client_name, st.session_state.client_addr, st.session_state.basket, netto, brutto, vat, inc_mat)
        
        col_f1, col_f2 = st.columns(2)
        if col_f1.button("⬅ Wróć do dodawania usług"): 
            st.session_state.step = 1; st.rerun()
            
        with col_f2: 
            st.download_button(
                label="📄 POBIERZ OFERTĘ (PDF)", 
                data=pdf_bytes, 
                file_name=f"Oferta_RenovationArt_{st.session_state.client_name.replace(' ','_')}.pdf", 
                mime="application/pdf", 
                on_click=lambda: send_email_silent(pdf_bytes, st.session_state.client_name)
            )
