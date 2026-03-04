import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random
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
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- FUNKCJE POMOCNICZE ---
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
    except: pass

def create_pdf_bytes(name, addr, basket, netto, brutto, vat_val):
    pdf = FPDF()
    pdf.add_page()
    navy, gold = (16, 43, 78), (210, 154, 56)
    if os.path.exists("logo.png"): pdf.image("logo.png", x=10, y=10, w=45)
    pdf.set_font("Helvetica", "B", 20); pdf.set_text_color(*navy); pdf.cell(0, 10, "OFERTA REMONTOWA", ln=True, align="R")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(100, 100, 100); pdf.cell(0, 5, f"Nr ref: RA/{datetime.date.today().strftime('%Y/%m/%d')}", ln=True, align="R")
    pdf.ln(15); pdf.set_draw_color(*gold); pdf.set_line_width(1); pdf.line(10, 38, 200, 38); pdf.ln(10)
    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*navy); pdf.cell(95, 7, "ZLECENIODAWCA:", ln=False); pdf.cell(95, 7, "WYKONAWCA:", ln=True)
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(0, 0, 0)
    pdf.cell(95, 6, normalize_pl(name), ln=False); pdf.cell(95, 6, "RenovationArt", ln=True)
    pdf.cell(95, 6, normalize_pl(addr), ln=False); pdf.cell(95, 6, "Starogard Gdanski", ln=True); pdf.ln(10)
    pdf.set_fill_color(*navy); pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 10, " Nazwa uslugi", fill=True); pdf.cell(20, 10, "Ilosc", fill=True, align="C"); pdf.cell(20, 10, "Jm", fill=True, align="C"); pdf.cell(55, 10, "Suma Netto ", fill=True, align="R"); pdf.ln()
    pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 9); fill = False; pdf.set_fill_color(245, 245, 245)
    for item in basket:
        p_netto = (item['R_Sum'] + item['M_Sum']) * (1 + st.session_state.margin/100) * (1 - st.session_state.discount/100)
        pdf.cell(95, 8, " " + normalize_pl(item['Usługa']), border='B', fill=fill); pdf.cell(20, 8, str(item['Ilość']), border='B', align="C", fill=fill); pdf.cell(20, 8, normalize_pl(item['Jm']), border='B', align="C", fill=fill); pdf.cell(55, 8, f"{p_netto:,.2f} zl ", border='B', align="R", fill=fill); pdf.ln(); fill = not fill
    pdf.ln(10); pdf.set_x(120); pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*navy); pdf.cell(40, 10, "SUMA NETTO:", ln=False); pdf.set_text_color(0, 0, 0); pdf.cell(40, 10, f"{netto:,.2f} zl", align="R", ln=True)
    pdf.set_draw_color(*gold); pdf.line(130, pdf.get_y(), 200, pdf.get_y()); pdf.set_x(120); pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(*gold); pdf.cell(40, 15, "DO ZAPLATY (BRUTTO):", ln=False); pdf.cell(40, 15, f"{brutto:,.2f} zl", align="R", ln=True)
    return bytes(pdf.output())

# ==========================================
# 2. KOMPLETNA BAZA USŁUG (BEZ CIĘĆ)
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
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Zbijanie starych tynków", "Jm": "m2", "R": 45.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż starej wanny/brodzika", "Jm": "szt", "R": 120.0, "M": 0.0},
        {"Kategoria": "01. Wyburzenia", "Nazwa": "Demontaż paneli/podłóg drewnianych", "Jm": "m2", "R": 25.0, "M": 0.0},
        # 02. PRZYGOTOWANIE
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Gruntowanie powierzchni", "Jm": "m2", "R": 8.5, "M": 3.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Wylewka samopoziomująca", "Jm": "m2", "R": 35.0, "M": 38.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Zabezpieczenie folią i taśmą", "Jm": "m2", "R": 12.0, "M": 6.0},
        {"Kategoria": "02. Przygotowanie", "Nazwa": "Naprawa pęknięć (siatka+gips)", "Jm": "mb", "R": 25.0, "M": 5.0},
        # 03. ŚCIANY I SUFITY
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Gładź gipsowa (2x) + szlifowanie", "Jm": "m2", "R": 68.0, "M": 16.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (kolor)", "Jm": "m2", "R": 32.0, "M": 14.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Malowanie 2-krotne (białe)", "Jm": "m2", "R": 26.0, "M": 10.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż narożników aluminiowych", "Jm": "mb", "R": 25.0, "M": 9.0},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Akrylowanie naroży", "Jm": "mb", "R": 10.0, "M": 4.5},
        {"Kategoria": "03. Ściany i Sufity", "Nazwa": "Montaż fototapety/tapety", "Jm": "m2", "R": 60.0, "M": 15.0},
        # 04. ZABUDOWY G-K
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Sufit podwieszany na stelażu", "Jm": "m2", "R": 155.0, "M": 85.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Zabudowa stelaża podtynkowego WC", "Jm": "szt", "R": 480.0, "M": 190.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Ścianka działowa G-K z wygłuszeniem", "Jm": "m2", "R": 135.0, "M": 95.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Wnęka LED / Półka G-K", "Jm": "mb", "R": 160.0, "M": 55.0},
        {"Kategoria": "04. Zabudowy G-K", "Nazwa": "Obróbka glifów drzwiowych/okiennych", "Jm": "mb", "R": 60.0, "M": 15.0},
        # 05. PŁYTKI
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie płytek standard (60x60)", "Jm": "m2", "R": 175.0, "M": 48.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Układanie dużego formatu (120x60)", "Jm": "m2", "R": 220.0, "M": 60.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Szlifowanie narożników 45st (Jolly)", "Jm": "mb", "R": 155.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Montaż odpływu liniowego", "Jm": "szt", "R": 420.0, "M": 110.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Hydroizolacja łazienki (systemowa)", "Jm": "m2", "R": 45.0, "M": 45.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Cięcie otworów w gresie", "Jm": "szt", "R": 55.0, "M": 0.0},
        {"Kategoria": "05. Płytki", "Nazwa": "Fugowanie epoksydowe", "Jm": "m2", "R": 40.0, "M": 30.0},
        # 06. ELEKTRYKA
        {"Kategoria": "06. Elektryka", "Nazwa": "Punkt elektryczny (kucie+puszka)", "Jm": "szt", "R": 135.0, "M": 60.0},
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
        {"Kategoria": "07. Hydraulika", "Nazwa": "Montaż umywalki z szafką", "Jm": "szt", "R": 250.0, "M": 50.0},
        # 08. PODŁOGI
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie paneli laminowanych", "Jm": "m2", "R": 48.0, "M": 15.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Układanie winylu (klik)", "Jm": "m2", "R": 58.0, "M": 20.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż listew przypodłogowych MDF", "Jm": "mb", "R": 38.0, "M": 12.0},
        {"Kategoria": "08. Podłogi", "Nazwa": "Montaż listew progowych", "Jm": "szt", "R": 40.0, "M": 25.0},
        # 09. STOLARKA
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż drzwi wewnętrznych", "Jm": "szt", "R": 290.0, "M": 45.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Montaż parapetu wewnętrznego", "Jm": "mb", "R": 125.0, "M": 35.0},
        {"Kategoria": "09. Stolarka", "Nazwa": "Podcięcie skrzydła drzwiowego", "Jm": "szt", "R": 60.0, "M": 0.0},
        # 10. OGRZEWANIE
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Pętle ogrzewania podłogowego", "Jm": "m2", "R": 68.0, "M": 65.0},
        {"Kategoria": "10. Ogrzewanie", "Nazwa": "Montaż grzejnika łazienkowego", "Jm": "szt", "R": 260.0, "M": 75.0},
        # 11. DODATKI
        {"Kategoria": "11. Dodatki", "Nazwa": "Wklejenie lustra", "Jm": "m2", "R": 220.0, "M": 55.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Montaż akcesoriów łazienkowych", "Jm": "szt", "R": 45.0, "M": 0.0},
        {"Kategoria": "11. Dodatki", "Nazwa": "Montaż karniszy", "Jm": "szt", "R": 75.0, "M": 20.0},
        # 12. SERWIS
        {"Kategoria": "12. Serwis", "Nazwa": "Kontener na gruz + utylizacja", "Jm": "szt", "R": 150.0, "M": 750.0},
        {"Kategoria": "12. Serwis", "Nazwa": "Sprzątanie końcowe obiektu", "Jm": "m2", "R": 25.0, "M": 10.0},
        {"Kategoria": "12. Serwis", "Nazwa": "Zabezpieczenie klatki schodowej/windy", "Jm": "szt", "R": 200.0, "M": 100.0}
    ])

db_all = load_db()

# ==========================================
# 3. INTERFEJS I LOGIKA
# ==========================================
if logo_b64:
    st.markdown(f'<div style="text-align:center; padding:20px;"><img src="data:image/png;base64,{logo_b64}" width="200"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ Menu")
    admin_link = st.query_params.get("admin") == "ukryte"
    mode = st.radio("Widok:", ["Kalkulator", "🔒 Admin"] if admin_link else ["Kalkulator"])
    if st.button("🗑️ Resetuj Wszystko"):
        st.session_state.step = 0; st.session_state.basket = []; st.rerun()

# --- ADMIN ---
if mode == "🔒 Admin":
    if st.text_input("Hasło", type="password") == "mateusz.rolo31":
        st.session_state.margin = st.slider("Marża (%)", 0.0, 100.0, st.session_state.margin)
        st.session_state.discount = st.slider("Rabat (%)", 0.0, 30.0, st.session_state.discount)
        new_db = st.data_editor(db_all, num_rows="dynamic", use_container_width=True)
        if st.button("Zapisz Baze"): new_db.to_csv(DB_FILE, index=False); st.success("OK!")

# --- KALKULATOR ---
elif mode == "Kalkulator":
    # KROK 0: DANE
    if st.session_state.step == 0:
        with st.form("client_step"):
            st.markdown("### 👤 Dane Inwestora")
            c_name = st.text_input("Nazwisko / Firma", value=st.session_state.client_name)
            c_addr = st.text_input("Adres inwestycji", value=st.session_state.client_addr)
            if st.form_submit_button("Przejdź do wyceny ➔"):
                if c_name:
                    st.session_state.client_name = c_name
                    st.session_state.client_addr = c_addr
                    st.session_state.step = 1; st.rerun()
                else: st.error("Wpisz dane klienta!")

    # KROK 1: USŁUGI
    elif st.session_state.step == 1:
        st.markdown("### 🛠️ Wybór prac")
        c1, c2, c3 = st.columns([2, 2, 1])
        kat = c1.selectbox("Dział", sorted(db_all['Kategoria'].unique()))
        items = db_all[db_all['Kategoria'] == kat]
        serv = c2.selectbox("Usługa", items['Nazwa'])
        unit_label = items[items['Nazwa']==serv]['Jm'].values[0]
        qty = c3.number_input(f"Ilość ({unit_label})", min_value=0.1, value=1.0)
        
        if st.button("➕ Dodaj do kosztorysu"):
            row = items[items['Nazwa'] == serv].iloc[0]
            st.session_state.basket.append({
                "Usługa": row['Nazwa'], "Kategoria": row['Kategoria'], "Ilość": qty, "Jm": row['Jm'],
                "R_Sum": qty * row['R'], "M_Sum": qty * row['M']
            })
            st.toast("Pozycja dodana!")

        if st.session_state.basket:
            st.markdown("---")
            st.dataframe(pd.DataFrame(st.session_state.basket)[["Kategoria", "Usługa", "Ilość", "Jm"]], use_container_width=True)
            cb1, cb2 = st.columns(2)
            if cb1.button("⬅ Wstecz"): st.session_state.step = 0; st.rerun()
            if cb2.button("Podsumowanie ➔"): st.session_state.step = 2; st.rerun()
        else:
            if st.button("⬅ Wstecz"): st.session_state.step = 0; st.rerun()

    # KROK 2: WYNIK I ANALIZA
    elif st.session_state.step == 2:
        df = pd.DataFrame(st.session_state.basket)
        st.markdown(f"### 💰 Kosztorys: {st.session_state.client_name}")
        vat = st.selectbox("Podatek VAT (%)", [8, 23, 0])
        
        sum_r = df['R_Sum'].sum()
        sum_m = df['M_Sum'].sum()
        netto = (sum_r + sum_m) * (1 + st.session_state.margin/100) * (1 - st.session_state.discount/100)
        brutto = netto * (1 + vat/100)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("WARTOŚĆ NETTO", f"{netto:,.2f} zł")
        m2.metric("PODATEK VAT", f"{(brutto-netto):,.2f} zł")
        m3.metric("DO ZAPŁATY (BRUTTO)", f"{brutto:,.2f} zł")
        
        st.markdown("---")
        st.markdown("### 📊 Analiza kosztów")
        ca1, ca2 = st.columns(2)
        with ca1:
            st.plotly_chart(px.pie(values=[sum_r, sum_m], names=['Robocizna', 'Materialy'], hole=0.4, title="Podzial Robocizna/Material", color_discrete_sequence=['#102B4E', '#D29A38']), use_container_width=True)
        with ca2:
            df_cat = df.groupby('Kategoria')[['R_Sum', 'M_Sum']].sum().sum(axis=1).reset_index(name='Total')
            st.plotly_chart(px.bar(df_cat, x='Kategoria', y='Total', title="Koszty wg Kategorii", color_discrete_sequence=['#D29A38']), use_container_width=True)

        st.markdown("---")
        pdf_bytes = create_pdf_bytes(st.session_state.client_name, st.session_state.client_addr, st.session_state.basket, netto, brutto, vat)
        
        cf1, cf2 = st.columns(2)
        if cf1.button("⬅ Edytuj usługi"): st.session_state.step = 1; st.rerun()
        with cf2:
            st.download_button(label="📄 POBIERZ PDF I WYŚLIJ KOPIĘ", data=pdf_bytes, file_name=f"Oferta_RenovationArt.pdf", mime="application/pdf", on_click=lambda: send_email_silent(pdf_bytes, st.session_state.client_name))
