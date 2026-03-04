import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os

# ==========================================
# 1. KONFIGURACJA STRONY I DESIGN (CSS MAX)
# ==========================================
st.set_page_config(page_title="RenovationArt | System Ofert", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

# --- EKSTREMALNY CSS (Level MAX) ---
custom_css = """
<style>
    /* 1. Import eleganckiej czcionki z Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

    /* 2. Zmiana globalnego fontu i tła aplikacji */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    .stApp {
        background-color: #F4F7F9; /* Delikatna, chłodna szarość premium */
    }

    /* 3. Ukrywanie śmieci Streamlita i resetowanie paddingów */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px; /* Zwężenie layoutu dla lepszej czytelności */
    }

    /* 4. Pływający Baner RenovationArt */
    .premium-banner {
        background: linear-gradient(135deg, #102B4E 0%, #0a1b33 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        border-bottom: 5px solid #D29A38;
        box-shadow: 0 10px 30px rgba(16,43,78,0.15);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .premium-banner h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .premium-banner p {
        color: #D29A38;
        margin: 10px 0 0 0;
        font-weight: 500;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    /* 5. Modernizacja zakładek (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eef2f5;
        font-weight: 600;
        color: #5E6E85;
    }
    .stTabs [aria-selected="true"] {
        background-color: #102B4E !important;
        color: #D29A38 !important;
        border-color: #102B4E !important;
        box-shadow: 0 4px 15px rgba(16,43,78,0.2);
    }
    
    /* 6. Zaokrąglone pola tekstowe z akcentem */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #e0e6ed !important;
        padding: 10px !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.02) !important;
        transition: all 0.3s;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #D29A38 !important;
        box-shadow: 0 0 0 1px #D29A38 !important;
    }

    /* 7. Przyciski z efektem Premium */
    div.stButton > button {
        background-color: #102B4E;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px rgba(16,43,78,0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #D29A38;
        color: #102B4E;
        box-shadow: 0 6px 12px rgba(210,154,56,0.3);
        transform: translateY(-2px);
    }

    /* 8. Metryki (Karty podsumowania) */
    [data-testid="stMetric"] {
        background-color: white;
        border-left: 6px solid #D29A38;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #5E6E85 !important;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #102B4E !important;
        font-weight: 700;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- WIDOCZNY BANER ---
st.markdown("""
<div class="premium-banner">
    <h1>RenovationArt</h1>
    <p>PROFESJONALNY SYSTEM WYCEN</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# RESZTA LOGIKI (BAZA, FUNKCJE, UI)
# ==========================================
DB_FILE = "baza_cen.csv"

def load_database():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        data = [
            {"Kategoria": "Prace wyburzeniowe", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "Cena_Robocizna": 50.0, "Cena_Material": 0.0},
            {"Kategoria": "Prace przygotowawcze", "Nazwa": "Gruntowanie podłoża", "Jm": "m2", "Cena_Robocizna": 8.0, "Cena_Material": 2.5},
            {"Kategoria": "Malowanie i Gładzie", "Nazwa": "Gładź gipsowa (2-krotna + szlifowanie)", "Jm": "m2", "Cena_Robocizna": 60.0, "Cena_Material": 12.0},
            {"Kategoria": "Malowanie i Gładzie", "Nazwa": "Malowanie dwukrotne (ściany/sufity)", "Jm": "m2", "Cena_Robocizna": 25.0, "Cena_Material": 8.0},
            {"Kategoria": "Zabudowa G-K", "Nazwa": "Sufit podwieszany prosty na stelażu", "Jm": "m2", "Cena_Robocizna": 160.0, "Cena_Material": 65.0},
            {"Kategoria": "Płytki", "Nazwa": "Układanie glazury/terakoty (standard)", "Jm": "m2", "Cena_Robocizna": 160.0, "Cena_Material": 35.0},
            {"Kategoria": "Płytki", "Nazwa": "Układanie wielkiego formatu (np. 120x60)", "Jm": "m2", "Cena_Robocizna": 230.0, "Cena_Material": 45.0},
            {"Kategoria": "Podłogi", "Nazwa": "Układanie paneli laminowanych/winylowych", "Jm": "m2", "Cena_Robocizna": 45.0, "Cena_Material": 15.0},
            {"Kategoria": "Elektryka", "Nazwa": "Punkt elektryczny (kucie, kabel, puszka)", "Jm": "szt", "Cena_Robocizna": 120.0, "Cena_Material": 40.0},
            {"Kategoria": "Hydraulika", "Nazwa": "Punkt wodno-kanalizacyjny", "Jm": "szt", "Cena_Robocizna": 350.0, "Cena_Material": 90.0}
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
    pdf.cell(0, 10, normalize_text("OFERTA CENOWA / KOSZTORYS"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=10)
    pdf.cell(100, 6, normalize_text(f"Wykonawca: RenovationArt"), new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 6, normalize_text(f"Data oferty: {datetime.date.today()}"), new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.cell(100, 6, normalize_text(f"Klient: {client['imie_nazwisko']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 6, normalize_text(f"Adres inwestycji: {client['adres']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 6, normalize_text(f"Planowany termin: {client['termin']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font("helvetica", style="B", size=9)
    col_widths = [10, 80, 15, 20, 30, 35]
    headers = ["Lp", "Nazwa uslugi", "Jm", "Ilosc", "Cena Jedn(Netto)", "Wartosc(Netto)"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align="C")
    pdf.ln()
    
    pdf.set_font("helvetica", size=9)
    for idx, item in enumerate(st.session_state.pozycje_oferty):
        pdf.cell(col_widths[0], 8, str(idx+1), border=1, align="C")
        pdf.cell(col_widths[1], 8, normalize_text(item['Nazwa']), border=1)
        pdf.cell(col_widths[2], 8, normalize_text(item['Jm']), border=1, align="C")
        pdf.cell(col_widths[3], 8, str(item['Ilość']), border=1, align="C")
        cena_j = item['Cena_Robocizna'] + item['Cena_Material']
        wartosc = item['Wartość_Robocizna'] + item['Wartość_Materiał']
        pdf.cell(col_widths[4], 8, f"{cena_j:.2f} PLN", border=1, align="R")
        pdf.cell(col_widths[5], 8, f"{wartosc:.2f} PLN", border=1, align="R")
        pdf.ln()
    
    pdf.ln(10)
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(140, 8, normalize_text("Suma bazowa (Robocizna + Materialy):"), align="R")
    pdf.cell(50, 8, f"{totals['suma_bazowa']:.2f} PLN", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", size=10)
    pdf.cell(140, 6, normalize_text(f"Marza ({st.session_state.financials['marza_proc']}%):"), align="R")
    pdf.cell(50, 6, f"+ {totals['marza_kwota']:.2f} PLN", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(140, 6, normalize_text(f"Rabat ({st.session_state.financials['rabat_proc']}%):"), align="R")
    pdf.cell(50, 6, f"- {totals['rabat_kwota']:.2f} PLN", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(140, 8, normalize_text("SUMA NETTO:"), align="R")
    pdf.cell(50, 8, f"{totals['suma_netto']:.2f} PLN", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", size=10)
    pdf.cell(140, 6, normalize_text(f"Podatek VAT ({st.session_state.financials['vat_proc']}%):"), align="R")
    pdf.cell(50, 6, f"+ {totals['vat_kwota']:.2f} PLN", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(140, 10, normalize_text("DO ZAPLATY BRUTTO:"), align="R")
    pdf.cell(50, 10, f"{totals['suma_brutto']:.2f} PLN", align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(30)
    pdf.set_font("helvetica", size=10)
    pdf.cell(95, 10, normalize_text("...................................................."), align="C")
    pdf.cell(95, 10, normalize_text("...................................................."), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(95, 5, normalize_text("Podpis Wykonawcy"), align="C")
    pdf.cell(95, 5, normalize_text("Podpis Zleceniodawcy"), align="C", new_x="LMARGIN", new_y="NEXT")
    
    return pdf.output()

# ==========================================
# PASEK BOCZNY I NAWIGACJA
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
        if st.button("🗑️ Wyczyść cały kosztorys"):
            st.session_state.pozycje_oferty = []
            st.rerun()

# ==========================================
# GŁÓWNA APLIKACJA
# ==========================================
if tryb_aplikacji == "📝 Kalkulator Ofert":
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Dane Klienta", "🛠️ Kreator Usług", "💰 Wycena i Finanse", "📊 Analityka"])

    with tab1:
        st.markdown("### Krok 1: Wprowadź dane inwestycji")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.client_data["imie_nazwisko"] = st.text_input("Imię i Nazwisko / Nazwa Firmy", st.session_state.client_data["imie_nazwisko"])
            st.session_state.client_data["adres"] = st.text_input("Adres inwestycji", st.session_state.client_data["adres"])
        with col2:
            st.session_state.client_data["termin"] = st.date_input("Planowany termin", st.session_state.client_data["termin"])

    with tab2:
        st.markdown("### Krok 2: Skomponuj zakres prac")
        with st.container():
            col_cat, col_serv, col_qty, col_btn = st.columns([2, 3, 1, 1])
            with col_cat:
                kategorie = st.session_state.df_db['Kategoria'].unique()
                wybrana_kat = st.selectbox("Kategoria", kategorie)
            with col_serv:
                uslugi = st.session_state.df_db[st.session_state.df_db['Kategoria'] == wybrana_kat]['Nazwa'].tolist()
                wybrana_usluga = st.selectbox("Usługa", uslugi)
            with col_qty:
                ilosc = st.number_input("Ilość", min_value=0.1, value=1.0, step=1.0)
            with col_btn:
                st.write("") 
                st.write("")
                if st.button("➕ Dodaj"):
                    row = st.session_state.df_db[(st.session_state.df_db['Kategoria'] == wybrana_kat) & (st.session_state.df_db['Nazwa'] == wybrana_usluga)].iloc[0]
                    nowa_pozycja = {
                        "Kategoria": row['Kategoria'], "Nazwa": row['Nazwa'], "Jm": row['Jm'], "Ilość": ilosc,
                        "Cena_Robocizna": row['Cena_Robocizna'], "Cena_Material": row['Cena_Material'],
                        "Wartość_Robocizna": ilosc * row['Cena_Robocizna'], "Wartość_Materiał": ilosc * row['Cena_Material']
                    }
                    st.session_state.pozycje_oferty.append(nowa_pozycja)
                    st.toast('Pozycja dodana!', icon='✅')

        st.markdown("<br><h4>Twoja lista usług:</h4>", unsafe_allow_html=True)
        if st.session_state.pozycje_oferty:
            df_display = pd.DataFrame(st.session_state.pozycje_oferty)[['Kategoria', 'Nazwa', 'Ilość', 'Jm', 'Wartość_Robocizna', 'Wartość_Materiał']].copy()
            df_display['Wartość Całkowita'] = df_display['Wartość_Robocizna'] + df_display['Wartość_Materiał']
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("Koszyk jest pusty. Wybierz usługi z panelu powyżej.")

    with tab3:
        st.markdown("### Krok 3: Finanse i generowanie oferty")
        if st.session_state.pozycje_oferty:
            col_m, col_r, col_v = st.columns(3)
            with col_m:
                st.session_state.financials["marza_proc"] = st.number_input("Globalna Marża (%)", value=st.session_state.financials["marza_proc"], step=1.0)
            with col_r:
                st.session_state.financials["rabat_proc"] = st.number_input("Rabat dla klienta (%)", value=st.session_state.financials["rabat_proc"], step=1.0)
            with col_v:
                st.session_state.financials["vat_proc"] = st.selectbox("Stawka VAT (%)", options=[8.0, 23.0, 0.0], index=0 if st.session_state.financials["vat_proc"]==8.0 else 1)
            
            st.markdown("---")
            totals = calculate_totals()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Robocizna Baza", f"{totals['baza_robocizna']:.2f} zł")
            m2.metric("Materiał Baza", f"{totals['baza_material']:.2f} zł")
            m3.metric(f"Zysk (Marża +{st.session_state.financials['marza_proc']}%)", f"{totals['marza_kwota']:.2f} zł")
            m4.metric(f"Rabat (-{st.session_state.financials['rabat_proc']}%)", f"-{totals['rabat_kwota']:.2f} zł")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.info(f"**Suma Netto:**\n### {totals['suma_netto']:.2f} zł")
            c2.warning(f"**VAT ({st.session_state.financials['vat_proc']}%):**\n### {totals['vat_kwota']:.2f} zł")
            c3.success(f"**Do Zapłaty Brutto:**\n### {totals['suma_brutto']:.2f} zł")
            st.markdown("---")
            
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                pdf_bytes = generate_pdf()
                st.download_button("📄 Wygeneruj profesjonalny PDF", data=pdf_bytes, file_name=f"Oferta_{st.session_state.client_data['imie_nazwisko'].replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
            with col_dl2:
                csv = pd.DataFrame(st.session_state.pozycje_oferty).to_csv(index=False).encode('utf-8')
                st.download_button("📊 Pobierz zrzut CSV", data=csv, file_name="kosztorys.csv", mime="text/csv", use_container_width=True)
        else:
            st.warning("Musisz najpierw dodać usługi do wyceny w zakładce Kreator Usług.")

    with tab4:
        st.markdown("### Analiza rentowności")
        if st.session_state.pozycje_oferty:
            totals = calculate_totals()
            df_chart = pd.DataFrame({"Kategoria": ["Robocizna", "Materiały", "Marża"], "Wartość": [totals['baza_robocizna'], totals['baza_material'], totals['marza_kwota']]})
            fig = px.pie(df_chart, values='Wartość', names='Kategoria', hole=0.5, color_discrete_sequence=['#102B4E', '#D29A38', '#5E6E85'])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"💰 Szacowany zysk całkowity (Robocizna + Marża netto): **{(totals['baza_robocizna'] + totals['marza_kwota']):.2f} zł**")
        else:
            st.info("Brak danych do analizy rentowności.")

# ==========================================
# WIDOK 2: PANEL ADMINISTRATORA (ZABEZPIECZONY)
# ==========================================
elif tryb_aplikacji == "⚙️ Panel Administratora":
    st.markdown("## 🔐 Zarządzanie Cennikiem Usług")
    
    haslo = st.text_input("Wprowadź kod dostępu:", type="password")
    
    if haslo == "mateusz.rolo31":
        st.success("Dostęp autoryzowany.")
        st.markdown("Edytuj ceny bezpośrednio w komórkach. Aby dodać usługę, wpisz dane w ostatnim, pustym wierszu.")
        
        csv_backup = st.session_state.df_db.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Pobierz Backup Cennika (CSV)", data=csv_backup, file_name="baza_cen_backup.csv", mime="text/csv")
        
        st.markdown("---")
        
        edited_df = st.data_editor(
            st.session_state.df_db,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Cena_Robocizna": st.column_config.NumberColumn("Robocizna Netto", min_value=0.0, format="%.2f zł"),
                "Cena_Material": st.column_config.NumberColumn("Materiał Netto", min_value=0.0, format="%.2f zł"),
            }
        )
        
        if st.button("✅ Zapisz nowe ceny do bazy", type="primary"):
            edited_df.to_csv(DB_FILE, index=False)
            st.session_state.df_db = edited_df
            st.success("Baza zaktualizowana poprawnie!")
            
    elif haslo != "":
        st.error("❌ Odmowa dostępu.")
