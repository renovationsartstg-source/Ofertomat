import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64
import random

# ==========================================
# 1. KONFIGURACJA STRONY
# ==========================================
st.set_page_config(page_title="RenovationArt | System Wycen", page_icon="🏗️", layout="wide")

# Bezpieczna funkcja ładująca grafikę do Base64
def get_base64_of_image(file_name):
    try:
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None

# Ładowanie LOGO
logo_b64 = get_base64_of_image("logo.png")
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="brand-logo" alt="RenovationArt Logo">'
else:
    logo_html = '<h1 class="brand-title-text">RenovationArt</h1>'

# Losowanie JEDNEGO obrazu tła, żeby nie zawiesić przeglądarki!
dostepne_tla = [img for img in ["image1.png", "image2.png", "image3.png"] if os.path.exists(img)]
wylosowane_tlo = random.choice(dostepne_tla) if dostepne_tla else None
tlo_b64 = get_base64_of_image(wylosowane_tlo) if wylosowane_tlo else None

# Dynamiczne wstrzyknięcie tła do CSS
bg_css_rule = ""
if tlo_b64:
    # Używamy linear-gradient do nałożenia granatowego filtra na zdjęcie!
    bg_css_rule = f"background: linear-gradient(rgba(16,43,78,0.75), rgba(10,27,51,0.85)), url('data:image/png;base64,{tlo_b64}');"
else:
    bg_css_rule = "background: linear-gradient(135deg, #102B4E 0%, #0a1b33 100%);"

# ==========================================
# 2. DESIGN PREMIUM (CSS)
# ==========================================
premium_css = f"""
<style>
    /* Czcionka i tło aplikacji */
    @import url('
