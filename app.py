import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import datetime
import os
import base64

# ==========================================
# 1. KONFIGURACJA STRONY I LOGOWANIE GRAFIK (.PNG)
# ==========================================
st.set_page_config(page_title="RenovationArt | System Wycen", page_icon="🏗️", layout="wide")

def get_base64_of_image(file_name):
    """Bezpieczne ładowanie pliku z logiem do formatu Base64"""
    try:
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except Exception:
        pass
    return None

logo_b64 = get_base64_of_image("logo.png")
if logo_b64:
    logo_html = f'<img src="{logo_b64}" class="brand-logo" alt="RenovationArt Logo">'
else:
    logo_html = '<h1 class="brand-title-text">RenovationArt</h1>'

image1_base64 = get_base64_of_image("image1.png")
image2_base64 = get_base64_of_image("image2.png")
image3_base64 = get_base64_of_image("image3.png")

images_base64 = [img for img in [image1_base64, image2_base64, image3_base64] if img]

if not images_base64:
    images_html_background = '<div class="fallback-background"></div>'
else:
    images_html_background = ""
    for i, img in enumerate(images_base64):
        images_html_background += f'<img src="{img}" class="slide active-{i+1}">'

# ==========================================
# 2. EKSTREMALNY CSS (DESIGN PREMIUM)
# ==========================================
advanced_design_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
    .stApp { background-color: #F4F7F9; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .block-container { padding-top: 2rem !important; max-width: 1200px; }

    /* Animowany Baner */
    .animated-banner {
        position: relative;
        padding: 50px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 40px;
        border-bottom: 5px solid #D29A38;
        box-shadow: 0 10px 30px rgba(16,43,78,0.15);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(16,43,78,0.7); z-index: 1; border-radius: 12px;
    }
    .animated-banner .slideshow {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0;
    }
    .animated-banner .slide {
        position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0;
        animation: slideAnimation 18s infinite;
    }
    .active-1 { animation-delay: 0s; }
    .active-2 { animation-delay: 6s; }
    .active-3 { animation-delay: 12s; }

    @keyframes slideAnimation {
        0% { opacity: 0; } 5% { opacity: 1; } 25% { opacity: 1; } 33% { opacity: 0; } 100% { opacity: 0; }
    }
    .fallback-background {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, #102B4E 0%, #0a1b33 100%); z-index: 0; border-radius: 12px;
    }

    .banner-text-content { position: relative; z-index: 2; }
    .brand-logo { max-width: 320px; height: auto; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .brand-title-text { color: #ffffff !important; font-size: 3.2rem !important; margin: 0 !important; font-weight: 700 !important; }
    .animated-banner p { color: #D29A38; margin: 10px 0 0 0; font-weight: 600; font-size: 1.2rem; letter-spacing: 1px; text-transform: uppercase; }

    /* Zakładki, Przyciski, Pola */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 8px; padding: 10px 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); font-weight: 600; color: #5E6E85; border: 1px solid #eef2f5; }
    .stTabs [aria-selected="true"] { background-color: #102B4E !important; color: #D29A38 !important; border: 1px solid #102B4E !important; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { border-radius: 8px !important; }
    div.stButton > button { background-color: #102B4E !important; color: white !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100%; border: none !important;}
    div.stButton > button:hover { background-color: #D29A38 !important; color: #102B4E !important; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(210,154,56,0.3); }

    /* Metryki */
    [data-testid="stMetric"] { background-color: white; border-left: 5px solid #D29A38; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { color: #102B4E !important; font-weight: 700 !important; }
</style>
"""
st.markdown(advanced_design_css, unsafe_allow_html=True)

# Wyświetlenie animowanego banera
st.markdown(f"""
<div class="animated-banner">
    <div class="overlay"></div>
    <div class="slideshow">{images_html_background}</div>
    <div class="banner-text-content">
        {logo_html}
        <p>Profesjonalny System Wycen</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
