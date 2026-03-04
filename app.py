import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime

# ==========================================
# 1. KONFIGURACJA STRONY I INICJALIZACJA STANÓW
# ==========================================
st.set_page_config(page_title="Ofertomat PRO", page_icon="🏗️", layout="wide")

# Funkcja inicjalizująca stan sesji (Session State)
def init_session_state():
    if 'client_data' not in st.session_state:
        st.session_state.client_data = {"imie_nazwisko": "", "adres": "", "termin": datetime.date.today()}
    # ZMIANA: używamy 'pozycje_oferty' zamiast 'items', aby uniknąć błędu Pandas
    if 'pozycje_oferty' not in st.session_state:
        st.session_state.pozycje_oferty = [] # Lista słowników z wybranymi usługami
    if 'financials' not in st.session_state:
        st.session_state.financials = {"marza_proc": 10.0, "rabat_proc": 0.0, "vat_proc": 8.0}

init_session_state()

# ==========================================
# 2. BAZA DANYCH (MOCK) I FUNKCJE POMOCNICZE
# ==========================================
@st.cache_data
def load_database():
    """Symulacja bazy danych usług i materiałów."""
    data = [
        {"Kategoria": "Prace wyburzeniowe", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "Cena_Robocizna": 45.0, "Cena_Material": 0.0},
        {"Kategoria": "Elektryka", "Nazwa": "Wykonanie punktu elektrycznego", "Jm": "szt", "Cena_Robocizna": 110.0, "Cena_Material": 35.0},
        {"Kategoria": "Hydraulika", "Nazwa": "Podejście wod-kan", "Jm": "szt", "Cena_Robocizna": 300.0, "Cena_Material": 80.0},
        {"Kategoria": "Zabudowa G-K", "Nazwa": "Sufit podwieszany prosty", "Jm": "m2", "Cena_Robocizna": 140.0, "Cena_Material": 60.0},
        {"Kategoria": "Malowanie", "Nazwa": "Malowanie dwukrotne", "Jm": "m2", "Cena_Robocizna": 25.0, "Cena_Material": 4.5},
        {"Kategoria": "Płytki", "Nazwa": "Układanie glazury (standard)", "Jm": "m2", "Cena_Robocizna": 150.0, "Cena_Material": 25.0},
    ]
    return pd.DataFrame(data)

df_db = load_database()

def calculate_totals():
    """
    Kluczowa funkcja: Oblicza wszystkie podsumowania finansowe.
    Logika przeliczania marży i rabatu:
    1. Sumujemy bazowe koszty robocizny i materiałów.
    2. Marża (Narzut) dodawana jest do całości netto.
    3. Rabat odliczany jest od kwoty powiększonej o marżę.
    4. VAT naliczany jest na samym końcu od finalnej kwoty netto.
    """
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
        "baza_robocizna": baza_robocizna,
        "baza_material": baza_material,
        "suma_bazowa": suma_bazowa,
        "marza_kwota": marza_kwota,
        "rabat_kwota": rabat_kwota,
        "suma_netto": suma_netto,
        "vat_kwota": vat_kwota,
        "suma_brutto": suma_brutto
    }

def normalize_text(text):
    """Usuwa polskie znaki dla uproszczonego generowania PDF bez wgrywania zew. czcionek TTF."""
    replacements = {'ą':'a', 'ć':'c', 'ę':'e', 'ł':'l', 'ń':'n', 'ó':'o', 'ś':'s', 'ź':'z', 'ż':'z',
                    'Ą':'A', 'Ć':'C', 'Ę':'E', 'Ł':'L', 'Ń':'N', 'Ó':'O', 'Ś':'S', 'Ź':'Z', 'Ż':'Z'}
    for pl, asc in replacements.items():
        text = str(text).replace(pl, asc)
    return text

def generate_pdf():
    """Generowanie profesjonalnego pliku PDF z użyciem biblioteki FPDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    totals = calculate_totals()
    client = st.session_state.client_data
    
    # Nagłówek
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(0, 10, normalize_text("OFERTA CENOWA / KOSZTORYS"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Dane
    pdf.set_font("helvetica", size=10)
    pdf.cell(100, 6, normalize_text(f"Wykonawca: RenovationArt"), new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 6, normalize_text(f"Data oferty: {datetime.date.today()}"), new_x="LMARGIN", new_y="NEXT", align="R")
    
    pdf.cell(100, 6, normalize_text(f"Klient: {client['imie_nazwisko']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 6, normalize_text(f"Adres inwestycji: {client['adres']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 6, normalize_text(f"Planowany termin: {client['termin']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Tabela z pozycjami
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
    
    # Podsumowanie finansowe
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
    
    pdf.ln(15)
    pdf.set_font("helvetica", style="I", size=8)
    pdf.cell(0, 5, normalize_text("Powyzsza oferta ma charakter informacyjny i jest wazna przez 14 dni od daty wystawienia."), align="C")
    
    return pdf.output()

# ==========================================
# 3. INTERFEJS UŻYTKOWNIKA (UI)
# ==========================================

# Panel Boczny (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1004/1004114.png", width=100) # Placeholder na logo
    st.title("Ofertomat PRO")
    st.markdown("Wersja 1.0.1 | Panel Wykonawcy")
    
    st.markdown("---")
    if st.button("🧹 Wyczyść całą ofertę", type="secondary"):
        st.session_state.pozycje_oferty = []
        st.rerun()

# Główne Zakładki
tab1, tab2, tab3, tab4 = st.tabs(["👤 1. Dane Klienta", "🛠️ 2. Kreator Wyceny", "💰 3. Kosztorys i Finanse", "📊 4. Dashboard Analityczny"])

# --- ZAKŁADKA 1: DANE KLIENTA ---
with tab1:
    st.header("Informacje o projekcie")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.client_data["imie_nazwisko"] = st.text_input("Imię i Nazwisko / Nazwa Firmy", st.session_state.client_data["imie_nazwisko"])
        st.session_state.client_data["adres"] = st.text_input("Adres inwestycji", st.session_state.client_data["adres"])
    with col2:
        st.session_state.client_data["termin"] = st.date_input("Planowany termin realizacji", st.session_state.client_data["termin"])

# --- ZAKŁADKA 2: KREATOR WYCENY ---
with tab2:
    st.header("Dodaj usługi do kosztorysu")
    
    # Formularz dodawania pozycji
    with st.expander("➕ Rozwiń, aby dodać nową pozycję", expanded=True):
        col_cat, col_serv, col_qty, col_btn = st.columns([2, 3, 1, 1])
        
        with col_cat:
            kategorie = df_db['Kategoria'].unique()
            wybrana_kat = st.selectbox("Kategoria", kategorie)
            
        with col_serv:
            uslugi = df_db[df_db['Kategoria'] == wybrana_kat]['Nazwa'].tolist()
            wybrana_usluga = st.selectbox("Usługa", uslugi)
            
        with col_qty:
            ilosc = st.number_input("Ilość", min_value=0.1, value=1.0, step=1.0)
            
        with col_btn:
            st.write("") # Odstęp dla wyrównania z polami tekstowymi
            st.write("")
            if st.button("Dodaj do wyceny", type="primary", use_container_width=True):
                # Pobranie danych z bazy dla wybranej usługi
                row = df_db[(df_db['Kategoria'] == wybrana_kat) & (df_db['Nazwa'] == wybrana_usluga)].iloc[0]
                
                nowa_pozycja = {
                    "Kategoria": row['Kategoria'],
                    "Nazwa": row['Nazwa'],
                    "Jm": row['Jm'],
                    "Ilość": ilosc,
                    "Cena_Robocizna": row['Cena_Robocizna'],
                    "Cena_Material": row['Cena_Material'],
                    "Wartość_Robocizna": ilosc * row['Cena_Robocizna'],
                    "Wartość_Materiał": ilosc * row['Cena_Material']
                }
                st.session_state.pozycje_oferty.append(nowa_pozycja)
                st.success("Dodano!")

    # Wyświetlanie aktualnych pozycji w formie interaktywnej tabeli
    st.subheader("Bieżące pozycje w wycenie")
    if st.session_state.pozycje_oferty:
        df_items = pd.DataFrame(st.session_state.pozycje_oferty)
        # Formatowanie kolumn do wyświetlenia
        df_display = df_items[['Kategoria', 'Nazwa', 'Ilość', 'Jm', 'Wartość_Robocizna', 'Wartość_Materiał']].copy()
        df_display['Wartość Całkowita'] = df_display['Wartość_Robocizna'] + df_display['Wartość_Materiał']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Brak pozycji w kosztorysie. Użyj formularza powyżej, aby coś dodać.")

# --- ZAKŁADKA 3: KOSZTORYS I FINANSE ---
with tab3:
    st.header("Ustawienia Finansowe i Podsumowanie")
    
    if st.session_state.pozycje_oferty:
        # Panel ustawień finansowych
        col_m, col_r, col_v = st.columns(3)
        with col_m:
            st.session_state.financials["marza_proc"] = st.number_input("Globalna Marża (%)", value=st.session_state.financials["marza_proc"], step=1.0)
        with col_r:
            st.session_state.financials["rabat_proc"] = st.number_input("Rabat dla klienta (%)", value=st.session_state.financials["rabat_proc"], step=1.0)
        with col_v:
            st.session_state.financials["vat_proc"] = st.selectbox("Stawka VAT (%)", options=[8.0, 23.0, 0.0], index=0 if st.session_state.financials["vat_proc"]==8.0 else 1)

        st.markdown("---")
        
        # Wyliczenia i metryki
        totals = calculate_totals()
        
        st.subheader("Podsumowanie Wartości")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Baza Robocizna (Netto)", f"{totals['baza_robocizna']:.2f} zł")
        m2.metric("Baza Materiały (Netto)", f"{totals['baza_material']:.2f} zł")
        m3.metric(f"Marża (+{st.session_state.financials['marza_proc']}%)", f"{totals['marza_kwota']:.2f} zł")
        m4.metric(f"Rabat (-{st.session_state.financials['rabat_proc']}%)", f"-{totals['rabat_kwota']:.2f} zł")
        
        st.markdown("###")
        
        c1, c2, c3 = st.columns(3)
        c1.info(f"**Suma Netto:**\n### {totals['suma_netto']:.2f} zł")
        c2.warning(f"**VAT ({st.session_state.financials['vat_proc']}%):**\n### {totals['vat_kwota']:.2f} zł")
        c3.success(f"**Suma Brutto:**\n### {totals['suma_brutto']:.2f} zł")

        st.markdown("---")
        
        # Eksport danych
        st.subheader("📄 Eksport i Dokumenty")
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # Generowanie i pobieranie PDF
            pdf_bytes = generate_pdf()
            st.download_button(
                label="⬇️ Pobierz Ofertę (PDF)",
                data=pdf_bytes,
                file_name=f"Oferta_{st.session_state.client_data['imie_nazwisko'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_dl2:
            # Generowanie i pobieranie CSV
            csv = pd.DataFrame(st.session_state.pozycje_oferty).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Pobierz Kosztorys (CSV)",
                data=csv,
                file_name="kosztorys_szczegolowy.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.warning("Dodaj pozycje w zakładce Kreator Wyceny, aby zobaczyć podsumowanie finansowe.")

# --- ZAKŁADKA 4: DASHBOARD ANALITYCZNY ---
with tab4:
    st.header("Struktura kosztów projektu")
    
    if st.session_state.pozycje_oferty:
        totals = calculate_totals()
        
        # Przygotowanie danych do wykresu kołowego
        dane_wykres = {
            "Kategoria": ["Robocizna (Baza)", "Materiały (Baza)", "Marża (Twój zysk)"],
            "Wartość": [totals['baza_robocizna'], totals['baza_material'], totals['marza_kwota']]
        }
        df_chart = pd.DataFrame(dane_wykres)
        
        # Wykres z użyciem plotly
        fig = px.pie(
            df_chart, 
            values='Wartość', 
            names='Kategoria', 
            title="Udział kosztów w cenie Netto (przed rabatem)",
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'],
            hole=0.4 # Tworzy efekt "Donut chart" - nowocześniejszy wygląd
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Dodatkowa analiza - zysk całkowity
        st.info(f"💡 Twój szacowany zysk z tego zlecenia (Suma robocizny + Marża): **{(totals['baza_robocizna'] + totals['marza_kwota']):.2f} zł netto**")
    else:
        st.info("Dodaj pozycje do wyceny, aby wygenerować wykresy analityczne.")
