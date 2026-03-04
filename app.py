import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import random

# ==========================================
# 1. KONFIGURACJA STRONY I LEKKI CSS
# ==========================================
st.set_page_config(page_title="RenovationArt | System Wycen", page_icon="🏗️", layout="wide")

# Lekki CSS tylko do kolorystyki, czcionki i ukrycia znaczków Streamlit
clean_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
    .stApp { background-color: #F8F9FA; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Przyciski i Kafelki */
    div.stButton > button { background-color: #102B4E !important; color: white !important; font-weight: 600 !important; border-radius: 8px !important; border: 1px solid #102B4E !important; transition: all 0.3s; width: 100%;}
    div.stButton > button:hover { background-color: #D29A38 !important; border-color: #D29A38 !important; color: #102B4E !important; transform: translateY(-2px); }
    [data-testid="stMetric"] { background-color: white; border-left: 5px solid #D29A38; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { color: #102B4E !important; font-weight: 700 !important; }
</style>
"""
st.markdown(clean_css, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA BAZY DANYCH I STANÓW
# ==========================================
DB_FILE = "baza_cen.csv"

def load_database():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        data = [
            {"Kategoria": "Prace wyburzeniowe", "Nazwa": "Skuwanie glazury/terakoty", "Jm": "m2", "Cena_Robocizna": 50.0, "Cena_Material": 0.0},
            {"Kategoria": "Malowanie i Gładzie", "Nazwa": "Gładź gipsowa (2-krotna + szlifowanie)", "Jm": "m2", "Cena_Robocizna": 60.0, "Cena_Material": 12.0},
            {"Kategoria": "Zabudowa G-K", "Nazwa": "Sufit podwieszany prosty na stelażu", "Jm": "m2", "Cena_Robocizna": 160.0, "Cena_Material": 65.0},
            {"Kategoria": "Płytki", "Nazwa": "Układanie glazury/terakoty (standard)", "Jm": "m2", "Cena_Robocizna": 160.0, "Cena_Material": 35.0},
            {"Kategoria": "Podłogi", "Nazwa": "Układanie paneli laminowanych/winylowych", "Jm": "m2", "Cena_Robocizna": 45.0, "Cena_Material": 15.0},
            {"Kategoria": "Hydraulika", "Nazwa": "Punkt wodno-kanalizacyjny", "Jm": "szt", "Cena_Robocizna": 350.0, "Cena_Material": 90.0}
        ]
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE,
