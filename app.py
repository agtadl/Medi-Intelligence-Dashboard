"""
=========================================================================
 MEDIA INTELLIGENCE DASHBOARD — Minbite vs Arthada
=========================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# =========================================================================
# 1. PAGE CONFIG
# =========================================================================
st.set_page_config(
    page_title="Media Intelligence Dashboard | Minbite vs Arthada",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================
# 2. GLOBAL CONSTANTS & COLOR SYSTEM
#    (harmonized with the indigo / amber "glass" blur background)
# =========================================================================
BRAND_A, BRAND_B = "Minbite", "Arthada"

# High-contrast, non-clashing brand palette: cool indigo vs warm coral
BRAND_COLORS = {BRAND_A: "#4F46E5", BRAND_B: "#F97316"}

# Clear, standard-feeling sentiment palette (green/amber/red) with enough
# saturation to read well on both light glass cards and dark text
SENTIMENT_COLORS = {"Positif": "#22C55E", "Netral": "#FACC15", "Negatif": "#EF4444"}

# A varied, non-repeating multi-hue set for media type breakdowns
NEUTRAL_PALETTE = ["#4F46E5", "#0EA5E9", "#14B8A6", "#F97316", "#EC4899"]

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

# =========================================================================
# 3. CUSTOM CSS — clean / modern / Apple-like card layout
# =========================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: {FONT_FAMILY};
}}

/* ---------------- ONE single page-wide background ----------------
   This is intentionally the ONLY colored background in the whole app.
   The gradient lives ONLY on .stApp (the true outer canvas, which spans
   the full scrollable page height). [data-testid="stMain"] is its own
   scrollable region capped at viewport height with a default rounded
   card look -- painting it directly is what previously produced a
   purple box that stopped mid-page. Every nested wrapper below is
   forced fully transparent / square / shadow-less so .stApp's single
   gradient is the only color anyone ever sees. */
html, body, .stApp {{
    background: linear-gradient(160deg, #EEF1FF 0%, #F3F4F8 45%, #FFF8EE 100%) !important;
    background-attachment: fixed !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
.block-container {{
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
}}

/* Hide default streamlit chrome */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}}

/* ---------------- Top Navigation Bar (centered, first thing on page) ---------------- */
.stTabs {{
    margin-bottom: 18px !important;
}}
.stTabs [data-baseweb="tab-list"],
div[data-baseweb="tab-list"] {{
    gap: 6px !important;
    background: #FFFFFF !important;
    padding: 8px !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(20, 30, 60, 0.05) !important;
    width: fit-content !important;
    margin: 0 auto 18px auto !important;
    justify-content: center !important;
    border-bottom: none !important;
}}
.stTabs [data-baseweb="tab"],
div[data-baseweb="tab-list"] button {{
    background-color: transparent !important;
    border-radius: 10px !important;
    padding: 8px 22px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    color: #4A5468 !important;
    margin: 0 !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: #10182B !important;
    border-radius: 10px !important;
}}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] * {{
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}
/* Hilangkan garis indikator bawah (highlight bar) yang bawaan Streamlit */
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"],
div[data-baseweb="tab-highlight"],
div[data-baseweb="tab-border"] {{
    display: none !important;
    background: transparent !important;
    height: 0 !important;
}}
/* ---------------- Header row (transparent, no white card) ---------------- */
.dash-header {{
    background: transparent;
    padding: 8px 4px 26px 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
}}
.dash-header .dash-header-text {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
}}
.dash-header h1 {{
    font-size: 40px;
    font-weight: 800;
    color: #10182B;
    margin: 0;
    letter-spacing: -0.6px;
    line-height: 1.1;
}}
.dash-header p {{
    font-size: 15px;
    color: #5B6472;
    margin: 0;
    font-weight: 500;
}}

/* ---------------- Data points highlight box ---------------- */
.data-points-box {{
    background: linear-gradient(135deg, #10182B 0%, #1E2A4A 100%);
    color: #FFFFFF;
    border-radius: 20px;
    padding: 20px 42px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(16, 24, 43, 0.28);
    min-width: 220px;
}}
.data-points-box .dp-value {{
    font-size: 48px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -1px;
}}
.data-points-box .dp-label {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.4px;
    color: #A5B4FC;
    margin-top: 6px;
    text-transform: uppercase;
}}

/* ---------------- Shared glass-card look ----------------
   ONE single background gradient (declared above on the page itself).
   Every card below -- Quick Overview and all chart cards -- is just a
   translucent glass panel sitting on top of that one background; none of
   them paint their own separate color field, so there's no "double
   purple" layering anywhere on the page. */
.glass-card {{
    position: relative;
    border-radius: 20px;
    padding: 26px 30px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.65);
    box-shadow: 0 4px 18px rgba(20, 30, 60, 0.06);
    margin-bottom: 20px;
}}

.quick-overview {{
    /* inherits .glass-card; kept as its own class only for the qo-* children below */
}}
.qo-title {{
    position: relative; z-index: 2;
    font-size: 19px;
    font-weight: 800;
    color: #10182B;
    margin-bottom: 2px;
}}
.qo-subtitle {{
    position: relative; z-index: 2;
    font-size: 13px;
    color: #6B7280;
    font-weight: 500;
    margin-bottom: 22px;
}}
.qo-grid {{
    position: relative; z-index: 2;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}}
.qo-item {{
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-top: 3px solid #4F46E5;
    border-radius: 14px;
    padding: 16px 20px;
    flex: 1;
    min-width: 170px;
    transition: transform 0.15s ease;
}}
.qo-item:hover {{
    transform: translateY(-2px);
}}
.qo-item:nth-child(1) {{ border-top-color: #4F46E5; }}
.qo-item:nth-child(2) {{ border-top-color: #0EA5E9; }}
.qo-item:nth-child(3) {{ border-top-color: #22C55E; }}
.qo-item:nth-child(4) {{ border-top-color: #F97316; }}
.qo-value {{
    font-size: 25px;
    font-weight: 800;
    color: #10182B;
}}
.qo-value span {{
    font-size: 12px;
    font-weight: 600;
    color: #8A93A6;
    margin-left: 4px;
}}
.qo-label {{
    font-size: 12.5px;
    color: #5B6472;
    font-weight: 600;
    margin-top: 4px;
}}

/* ---------------- Chart card text labels (title/subtitle only) ---------------- */
.chart-title {{
    font-size: 15px;
    font-weight: 700;
    color: #10182B;
    margin-bottom: 0px;
}}
.chart-subtitle {{
    font-size: 11px;
    color: #9AA3B5;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

/* =========================================================================
   CHART CARD STYLING
   Every st.container(border=True) produces a div with
   data-testid="stVerticalBlockBorderWrapper". Styling that selector
   globally is fragile -- Streamlit sometimes wraps unrelated layout in the
   same test-id, which previously caused one giant accidental box to
   appear behind the whole page while the real chart cards stayed
   unstyled. To fix this for good we scope the glass style to ONLY the
   containers we explicitly mark: right before each st.container(border=True)
   we emit a tiny invisible ".chart-card-marker" element, and only the
   bordered wrapper that immediately follows one of those markers gets
   the glass treatment. Every other bordered wrapper stays fully
   transparent, so there is no stray box anywhere else on the page.
   ========================================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {{
    position: relative !important;
    background: rgba(255, 255, 255, 0.55) !important;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.65) !important;
    border-radius: 18px !important;
    padding: 18px 20px 14px 20px !important;
    margin-bottom: 18px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 18px rgba(20, 30, 60, 0.06) !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(20, 30, 60, 0.12) !important;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    padding: 0 !important;
    margin-bottom: 0 !important;
}}

/* ---------------- Insight box (explanation under each chart) ----------------
   High-contrast solid card so it never blends into the page/chart background. */
.insight-box {{
    position: relative;
    z-index: 2;
    background: #FFFFFF;
    border: 1px solid #E4E7F1;
    border-left: 4px solid #4F46E5;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0 4px 0;
    font-size: 13.5px;
    color: #1E2536;
    line-height: 1.6;
    box-shadow: 0 1px 6px rgba(20, 30, 60, 0.06);
}}
.insight-box b {{ color: #10182B; }}

/* ---------------- Section title ---------------- */
.section-title {{
    font-size: 19px;
    font-weight: 800;
    color: #10182B;
    margin: 6px 0 14px 0;
}}

/* Buttons */
div.stButton > button {{
    background-color: #10182B;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    font-size: 12.5px;
    padding: 6px 16px;
    border: none;
}}
div.stButton > button:hover {{
    background-color: #4F46E5;
    color: white;
}}

/* Conclusion card */
.conclusion-card {{
    background: #FFFFFF;
    border-radius: 16px;
    padding: 26px 28px;
    box-shadow: 0 2px 10px rgba(20, 30, 60, 0.05);
    margin-bottom: 18px;
}}
.winner-badge {{
    display: inline-block;
    background: #EEF2FF;
    color: #4338CA;
    font-weight: 700;
    font-size: 12px;
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 10px;
}}

/* ---------------- Text Input & Text Area (samain sama tema terang) ---------------- */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {{
    background-color: #FFFFFF !important;
    color: #10182B !important;
    border: 1px solid #E4E7F1 !important;
    border-radius: 10px !important;
}}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {{
    color: #9AA3B5 !important;
}}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {{
    color: #10182B !important;
    font-weight: 600 !important;
}}

/* ---------------- Paragraf & caption bawaan Streamlit ---------------- */
[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] {{
    color: #4B5568 !important;
}}
[data-testid="stMarkdownContainer"] h5 {{
    color: #10182B !important;
}}

/* ---------------- Timeline Table (HTML biasa, ganti data_editor) ---------------- */
.timeline-table {{
    width: 100%;
    border-collapse: collapse;
    background-color: #FFFFFF;
    border-radius: 12px;
    overflow: hidden;
    font-size: 13.5px;
    box-shadow: 0 4px 18px rgba(20, 30, 60, 0.06);
}}
.timeline-table th {{
    background-color: #F3F4F8;
    color: #10182B;
    font-weight: 700;
    text-align: left;
    padding: 10px 14px;
    border-bottom: 1px solid #E4E7F1;
}}
.timeline-table td {{
    background-color: #FFFFFF;
    color: #10182B;
    padding: 10px 14px;
    border-bottom: 1px solid #F0F1F5;
    vertical-align: top;
}}
.timeline-table tr:hover td {{
    background-color: #FAFAFC;
}}

/* ---------------- Timeline Table wrapper (scrollable) ---------------- */
.timeline-table-wrapper {{
    max-height: 480px;          /* atur sesuai selera, misal 400-600px */
    overflow-y: auto;
    border-radius: 12px;
    box-shadow: 0 4px 18px rgba(20, 30, 60, 0.06);
    margin-bottom: 12px;
}}
.timeline-table {{
    width: 100%;
    border-collapse: collapse;
    background-color: #FFFFFF;
    font-size: 13.5px;
}}
.timeline-table th {{
    position: sticky;
    top: 0;
    z-index: 1;
    background-color: #F3F4F8;
    color: #10182B;
    font-weight: 700;
    text-align: left;
    padding: 10px 14px;
    border-bottom: 1px solid #E4E7F1;
}}
.timeline-table td {{
    background-color: #FFFFFF;
    color: #10182B;
    padding: 10px 14px;
    border-bottom: 1px solid #F0F1F5;
    vertical-align: top;
}}
.timeline-table tr:hover td {{
    background-color: #FAFAFC;
}}

/* ---------------- st.info / st.warning box (biar senada juga) ---------------- */
div[data-testid="stAlert"] {{
    background-color: rgba(79, 70, 229, 0.08) !important;
    border-radius: 10px !important;
}}
div[data-testid="stAlert"] p {{
    color: #10182B !important;
}}


/* ---------------- st.info / st.warning box (biar senada juga) ---------------- */
div[data-testid="stAlert"] {{
    background-color: rgba(79, 70, 229, 0.08) !important;
    border-radius: 10px !important;
}}
div[data-testid="stAlert"] p {{
    color: #10182B !important;
}}

/* ---------------- st.dataframe (biar terang, senada tema) ---------------- */
div[data-testid="stDataFrame"] {{
    background-color: #FFFFFF !important;
}}
div[data-testid="stDataFrame"] * {{
    color: #10182B !important;
    background-color: #FFFFFF !important;
}}
div[data-testid="stDataFrame"] [role="columnheader"] {{
    background-color: #F3F4F8 !important;
    font-weight: 700 !important;
}}

/* ---------------- Sidebar: solid dark background ---------------- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #10182B 0%, #1E2A4A 100%) !important;
}}
section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
    background-color: rgba(255,255,255,0.06) !important;
    border: 1px dashed rgba(255,255,255,0.25) !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {{
    color: #C7CCDA !important;
}}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.15) !important;
}}

/* ---------------- FIX: caption/teks sidebar biar tetap terang di background gelap ---------------- */
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: #C7CCDA !important;
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {{
    color: #FFFFFF !important;
}}

/* ---------------- FIX: teks tombol "Generate AI Insight" biar putih jelas ---------------- */
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {{
    color: #FFFFFF !important;
}}

/* ---------------- Sidebar: solid dark background ---------------- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #10182B 0%, #1E2A4A 100%) !important;
}}
section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}

/* File uploader box di sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
    background-color: rgba(255,255,255,0.06) !important;
    border: 1px dashed rgba(255,255,255,0.25) !important;
}}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {{
    color: #C7CCDA !important;
}}

/* Text input & selectbox di sidebar */
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}

/* Divider (st.markdown("---")) di sidebar */
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.15) !important;
}}

</style>
""", unsafe_allow_html=True)

# =========================================================================
# 4. HELPER FUNCTIONS
# =========================================================================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalisasi nama kolom agar konsisten walaupun variasi ejaan/underscore."""
    rename_map = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "_")
        if key in ["brand"]:
            rename_map[col] = "Brand"
        elif key in ["date", "tanggal"]:
            rename_map[col] = "Date"
        elif key in ["platform"]:
            rename_map[col] = "Platform"
        elif key in ["sentiment", "sentimen"]:
            rename_map[col] = "Sentiment"
        elif key in ["location", "lokasi"]:
            rename_map[col] = "Location"
        elif key in ["engagements", "engagement"]:
            rename_map[col] = "Engagements"
        elif key in ["media_type", "mediatype", "media"]:
            rename_map[col] = "Media_Type"
        elif key in ["content_title", "title", "judul"]:
            rename_map[col] = "Content_Title"
        elif key in ["reason", "alasan"]:
            rename_map[col] = "Reason"
    df = df.rename(columns=rename_map)
    return df


@st.cache_data(show_spinner=False)
def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Data cleaning: normalisasi kolom, konversi Date, isi Engagements kosong dgn 0."""
    df = raw.copy()
    df = normalize_columns(df)

    required = ["Brand", "Date", "Platform", "Sentiment", "Location", "Engagements", "Media_Type"]
    for col in required:
        if col not in df.columns:
            df[col] = None

    # Konversi tanggal (support dd/mm/yyyy dan yyyy-mm-dd)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # Isi Engagements kosong dengan 0, pastikan integer
    df["Engagements"] = pd.to_numeric(df["Engagements"], errors="coerce").fillna(0).astype(int)

    # Bersihkan whitespace pada kolom kategorikal
    for col in ["Brand", "Platform", "Sentiment", "Location", "Media_Type"]:
        df[col] = df[col].astype(str).str.strip()

    df = df.dropna(subset=["Date"])
    return df


def call_openrouter(api_key: str, model: str, prompt: str) -> str:
    """Panggil OpenRouter API untuk menghasilkan insight otomatis."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": "Kamu adalah Media Intelligence Analyst. Jawab singkat, padat, berbasis data, dalam Bahasa Indonesia."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 450,
                "temperature": 0.4,
            }),
            timeout=40,
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Gagal memanggil API ({response.status_code}). Periksa API key / model."
    except Exception as e:
        return f"Terjadi error: {e}"


def insight_section(section_key: str, prompt: str, api_key: str, model: str, default_text: str = None):
    """Render tombol 'Generate Insight' + hasil AI, disimpan di session_state agar persist.
    Kalau default_text diisi dan belum ada hasil AI, default_text akan ditampilkan
    sebagai fallback sebelum user generate insight AI."""
    state_key = f"insight_{section_key}"
    if st.button("Generate AI Insight", key=f"btn_{section_key}"):
        if not api_key:
            st.warning("Masukkan OpenRouter API Key terlebih dahulu di sidebar.")
        else:
            with st.spinner("AI sedang menganalisis data..."):
                result = call_openrouter(api_key, model, prompt)
                st.session_state[state_key] = result

    if state_key in st.session_state:
        st.markdown(f'<div class="insight-box">{st.session_state[state_key]}</div>', unsafe_allow_html=True)
    elif default_text:
        st.markdown(f'<div class="insight-box">{default_text}</div>', unsafe_allow_html=True)


import contextlib


@contextlib.contextmanager
def chart_card():
    """Emits the invisible marker used by the CSS above, then opens a
    bordered container that the marker-scoped CSS turns into a glass card.
    Use exactly like st.container(border=True): `with chart_card(): ...`"""
    st.markdown('<div class="chart-card-marker"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        yield


def base_layout(fig, height=360):
    fig.update_layout(
        font=dict(family=FONT_FAMILY, color="#10182B", size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(color="#10182B", size=12),
            bgcolor="rgba(255,255,255,0.65)",
            bordercolor="rgba(16,24,43,0.08)",
            borderwidth=1,
        ),
        xaxis=dict(color="#10182B", tickfont=dict(color="#38415A")),
        yaxis=dict(color="#10182B", tickfont=dict(color="#38415A")),
    )
    return fig


def render_header(data_count: int, brand_a_name: str, brand_b_name: str):
    """Transparent title row + a big, boxed 'data points' highlight."""
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-header-text">
            <h1>Media Intelligence Dashboard</h1>
            <p>Comparative Digital Strategy Audit — {brand_a_name} vs {brand_b_name}</p>
        </div>
        <div class="data-points-box">
            <div class="dp-value">{data_count:,}</div>
            <div class="dp-label">Data Points</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================================
# 5. SIDEBAR — upload data & AI config
# =========================================================================
with st.sidebar:
    st.markdown("### Data Source")
    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
    st.caption("Dashboard sudah menampilkan data default. Upload CSV di sini kalau ingin mengganti dengan dataset lain (kolom wajib: Brand, Date, Platform, Sentiment, Location, Engagements, Media_Type).")

    st.markdown("---")
    st.markdown("### AI Insight Engine")
    st.caption("Didukung oleh OpenRouter")
    api_key = st.secrets["OPENROUTER_API_KEY"]
    model = st.selectbox(
    "Pilih Model AI",
    [
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-haiku",
        "google/gemini-2.0-flash-001",
        "meta-llama/llama-3.1-8b-instruct",
    ],
)
    st.markdown("---")
    st.caption("Media Intelligence Dashboard · UAS Project")


# =========================================================================
# 6. LOAD & CLEAN DATA
# =========================================================================
import os

DEFAULT_DATASET_PATH = "dataset.csv"

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
elif os.path.exists(DEFAULT_DATASET_PATH):
    raw_df = pd.read_csv(DEFAULT_DATASET_PATH)
else:
    st.markdown("""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 60vh;
        padding: 40px;
    ">
        <div style="font-size: 20px; font-weight: 700; color: #10182B; margin-bottom: 8px;">
            Belum ada data untuk ditampilkan
        </div>
        <div style="font-size: 14px; color: #8A93A6; max-width: 460px; line-height: 1.6;">
            Silakan upload file CSV kamu di sidebar untuk memulai analisis.<br>
            Kolom wajib: <b>Brand, Date, Platform, Sentiment, Location, Engagements, Media_Type</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = clean_data(raw_df)

if df.empty:
    st.error("Data tidak valid / kosong setelah proses cleaning. Periksa kembali file CSV kamu.")
    st.stop()

brands_available = sorted(df["Brand"].unique().tolist())
brand_a = brands_available[0] if len(brands_available) > 0 else BRAND_A
brand_b = brands_available[1] if len(brands_available) > 1 else BRAND_B
color_map = {brand_a: BRAND_COLORS[BRAND_A], brand_b: BRAND_COLORS[BRAND_B]}


# =========================================================================
# 7. TOP NAVIGATION — the very first thing on the page, centered
# =========================================================================
tab1, tab2, tab3 = st.tabs(["Dashboard", "Video Analysis (ABCD)", "Conclusion & Recommendation"])


# -------------------------------------------------------------------------
# TAB 1 — DASHBOARD (Quick Overview + 5 grafik komparatif,
#          setiap chart dibungkus glass box masing-masing)
# -------------------------------------------------------------------------
with tab1:

    render_header(len(df), brand_a, brand_b)

    # ==================== KPI ROW (Quick Overview - glass style) ====================
    total_engagement = df["Engagements"].sum()
    total_posts = len(df)
    positive_rate = (df["Sentiment"].str.lower().str.contains("posit").sum() / total_posts * 100) if total_posts else 0
    leading_brand = df.groupby("Brand")["Engagements"].sum().idxmax()

    engagement_display = f"{total_engagement/1_000_000:.1f}M" if total_engagement >= 1_000_000 else f"{total_engagement:,}"
    brand_a_share = (df[df["Brand"] == brand_a]["Engagements"].sum() / total_engagement * 100) if total_engagement else 0
    brand_b_share = 100 - brand_a_share

    st.markdown(f"""
    <div class="glass-card quick-overview">
        <div class="qo-title">Quick Overview</div>
        <div class="qo-subtitle">Ringkasan performa gabungan {brand_a} vs {brand_b}</div>
        <div class="qo-grid">
            <div class="qo-item">
                <div class="qo-value">{engagement_display}</div>
                <div class="qo-label">Total Engagements</div>
            </div>
            <div class="qo-item">
                <div class="qo-value">{total_posts}<span>posts</span></div>
                <div class="qo-label">Total Postingan</div>
            </div>
            <div class="qo-item">
                <div class="qo-value">{positive_rate:.1f}%</div>
                <div class="qo-label">Sentimen Positif</div>
            </div>
            <div class="qo-item">
                <div class="qo-value">{leading_brand}</div>
                <div class="qo-label">Leading Brand ({max(brand_a_share, brand_b_share):.0f}% share)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==================== CHART 1: Sentiment Breakdown ====================
    st.markdown('<div class="section-title">Sentiment Breakdown</div>', unsafe_allow_html=True)
    with chart_card():
        st.markdown('<div class="chart-subtitle">Opini Publik</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        for col, brand in zip([c1, c2], [brand_a, brand_b]):
            with col:
                st.markdown(f'<div class="chart-title">{brand}</div>', unsafe_allow_html=True)
                sub = df[df["Brand"] == brand]
                sent_counts = sub["Sentiment"].value_counts().reset_index()
                sent_counts.columns = ["Sentiment", "Count"]
                fig = go.Figure(data=[go.Pie(
                    labels=sent_counts["Sentiment"],
                    values=sent_counts["Count"],
                    hole=0.62,
                    marker=dict(colors=[SENTIMENT_COLORS.get(s, "#94A3B8") for s in sent_counts["Sentiment"]]),
                    textinfo="percent",
                    textfont=dict(size=12, color="white"),
                )])
                fig.update_layout(showlegend=True)
                st.plotly_chart(base_layout(fig, 300), use_container_width=True, key=f"sent_{brand}")

    sentiment_summary = df.groupby(["Brand", "Sentiment"])["Engagements"].agg(["count", "sum"]).reset_index()
    insight_section(
        "sentiment",
        f"Berikut ringkasan distribusi sentimen dua brand dalam data media intelligence:\n{sentiment_summary.to_string(index=False)}\n\nBerikan TEPAT 3 insight singkat (masing-masing 1 kalimat) berbentuk bullet point tentang perbandingan sentimen kedua brand ini, sebutkan merek mana yang lebih disukai publik dan mengapa.",
        api_key, model,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ==================== CHART 2: Engagement Trend Over Time ====================
    st.markdown('<div class="section-title">Engagement Trend Over Time</div>', unsafe_allow_html=True)
    with chart_card():
        # Only look at the last 12 months, anchored on today's real date --
        # this keeps the chart to "the past year" even if the CSV contains
        # stray/mistyped future or past dates that would otherwise stretch
        # the x-axis out to something like 2055.
        today = pd.Timestamp.now().normalize()
        one_year_ago = today - pd.DateOffset(years=1)
        df_trend_window = df[(df["Date"] >= one_year_ago) & (df["Date"] <= today)]
        trend = df_trend_window.groupby([pd.Grouper(key="Date", freq="W"), "Brand"])["Engagements"].sum().reset_index()

        fig2 = go.Figure()
        for brand in [brand_a, brand_b]:
            b_trend = trend[trend["Brand"] == brand].sort_values("Date")
            fig2.add_trace(go.Scatter(
                x=b_trend["Date"],
                y=b_trend["Engagements"],
                name=brand,
                mode="lines",
                line=dict(width=3, shape="spline", smoothing=1.1, color=color_map[brand]),
                fill="tozeroy",
                hovertemplate="%{y:,.0f}<extra>" + brand + "</extra>",
            ))
        # soft area fill under each line, matching the Google-Trends look
        for trace, brand in zip(fig2.data, [brand_a, brand_b]):
            hex_c = color_map[brand].lstrip("#")
            r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
            trace.fillcolor = f"rgba({r},{g},{b},0.08)"

        fig2.update_layout(
            xaxis_title=None,
            yaxis_title="Total Engagements",
            hovermode="x unified",
        )
        fig2.update_xaxes(showgrid=False, showline=True, linecolor="rgba(16,24,43,0.15)")
        fig2.update_yaxes(showgrid=True, gridcolor="rgba(16,24,43,0.08)", zeroline=False)
        st.plotly_chart(base_layout(fig2, 340), use_container_width=True, key="trend_chart")

    trend_summary = trend.pivot(index="Date", columns="Brand", values="Engagements").fillna(0).describe().to_string()
    insight_section(
        "trend",
        f"Berikut statistik tren engagement mingguan kedua brand:\n{trend_summary}\n\nBerikan TEPAT 3 insight singkat (1 kalimat tiap poin) tentang pola/tren engagement kedua brand dari waktu ke waktu, termasuk apakah ada lonjakan (spike) yang mencolok.",
        api_key, model,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ==================== CHART 3: Platform Engagements ====================
    st.markdown('<div class="section-title">Platform Engagements</div>', unsafe_allow_html=True)
    with chart_card():
        platform_data = df.groupby(["Platform", "Brand"])["Engagements"].sum().reset_index()
        fig3 = px.bar(
            platform_data, x="Platform", y="Engagements", color="Brand",
            barmode="group", color_discrete_map=color_map,
        )
        fig3.update_traces(marker_line_width=0)
        fig3.update_layout(xaxis_title=None, yaxis_title="Total Engagements")
        fig3.update_xaxes(showgrid=False)
        fig3.update_yaxes(showgrid=True, gridcolor="rgba(16,24,43,0.08)")
        st.plotly_chart(base_layout(fig3, 320), use_container_width=True, key="platform_chart")

    insight_section(
        "platform",
        f"Berikut total engagement per platform dan brand:\n{platform_data.to_string(index=False)}\n\nBerikan TEPAT 3 insight singkat (1 kalimat tiap poin) tentang platform mana yang paling mendominasi untuk masing-masing brand dan implikasinya bagi strategi media.",
        api_key, model,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ==================== CHART 4: Media Type Mix ====================
    st.markdown('<div class="section-title">Media Type Mix</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    for col, brand in zip([c3, c4], [brand_a, brand_b]):
        with col:
            with chart_card():
                st.markdown(f'<div class="chart-subtitle">Format Konten</div><div class="chart-title">{brand}</div>', unsafe_allow_html=True)
                sub = df[df["Brand"] == brand]
                media_counts = sub["Media_Type"].value_counts().reset_index()
                media_counts.columns = ["Media_Type", "Count"]
                fig4 = go.Figure(data=[go.Pie(
                    labels=media_counts["Media_Type"],
                    values=media_counts["Count"],
                    hole=0.55,
                    marker=dict(colors=NEUTRAL_PALETTE),
                    textinfo="percent",
                    textfont=dict(size=12, color="white"),
                )])
                st.plotly_chart(base_layout(fig4, 300), use_container_width=True, key=f"media_{brand}")

    media_summary = df.groupby(["Brand", "Media_Type"])["Engagements"].agg(["count", "sum"]).reset_index()
    insight_section(
        "media_type",
        f"Berikut ringkasan jenis konten (media type) yang digunakan kedua brand:\n{media_summary.to_string(index=False)}\n\nBerikan TEPAT 3 insight singkat (1 kalimat tiap poin) tentang format konten mana yang paling efektif untuk masing-masing brand.",
        api_key, model,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ==================== CHART 5: Top 5 Locations ====================
    st.markdown('<div class="section-title">Top 5 Locations by Engagement</div>', unsafe_allow_html=True)
    with chart_card():
        loc_data = df.groupby("Location")["Engagements"].sum().nlargest(5).reset_index()
        fig5 = px.bar(
            loc_data, x="Location", y="Engagements",
            color="Location",
            color_discrete_sequence=NEUTRAL_PALETTE,
        )
        fig5.update_traces(marker_line_width=0)
        fig5.update_layout(xaxis_title=None, yaxis_title="Total Engagements", showlegend=False)
        fig5.update_xaxes(showgrid=False)
        fig5.update_yaxes(showgrid=True, gridcolor="rgba(16,24,43,0.08)")
        st.plotly_chart(base_layout(fig5, 320), use_container_width=True, key="location_chart")

    insight_section(
        "locations",
        f"Berikut 5 lokasi dengan total engagement tertinggi secara keseluruhan:\n{loc_data.to_string(index=False)}\n\nBerikan TEPAT 3 insight singkat (1 kalimat tiap poin) tentang sebaran geografis audiens dan rekomendasi target lokasi untuk kampanye berikutnya.",
        api_key, model,
    )


# -------------------------------------------------------------------------
# TAB 2 — VIDEO ANALYSIS (Framework ABCD)
# -------------------------------------------------------------------------
with tab2:
    render_header(len(df), brand_a, brand_b)

    st.markdown('<div class="section-title">Audit Iklan Video — Framework ABCD</div>', unsafe_allow_html=True)
    st.caption("Analisis video kampanye dari brand yang unggul di Bagian 2, dievaluasi menggunakan Google AI Studio.")

    youtube_url = st.text_input("Tempel link YouTube video kampanye di sini", value="https://youtu.be/sv1XMvvKQTY?si=JJHFw8ueY56opW6W", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url:
        st.video(youtube_url)
    else:
        st.info("Masukkan link YouTube video kampanye organik/komersial dari brand pemenang untuk ditampilkan di sini.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Tabel Kronologis (Breakdown per Menit)")
    st.caption("Isi hasil ekstraksi dari Google AI Studio (unggah video → prompt breakdown menit-per-menit).")

    default_timeline = pd.DataFrame({
        "Waktu": [
            "00:00", "00:18", "00:37", "01:21", "01:35", "01:52", "02:11", "03:25",
            "05:08", "06:06", "06:33", "08:25", "09:51", "12:46", "14:12", "15:42",
            "16:55", "18:41", "20:47", "21:14", "23:23", "25:52", "27:14", "29:50",
            "31:41", "32:03",
        ],
        "Adegan": [
            "Cuplikan pembuka menampilkan Arthada menyanyi salawat.",
            "Intro animasi program \"Slay & Say\" menampilkan host Mochamado.",
            "Host (Mochamado dan rekan) menyapa penonton dan memperkenalkan tamu.",
            "Arthada duduk di sofa pink, host memintanya memperkenalkan diri.",
            "Arthada melakukan perkenalan diri dengan sangat cepat.",
            "Diskusi tentang gaya bicara \"sombong\" Arthada yang viral.",
            "Arthada menjelaskan asal usul gaya bicaranya yang cepat.",
            "Arthada bercerita tentang \"Ayam\" yang memaksanya bicara cepat saat ngonten.",
            "Cerita tentang lingkungan tempat tinggal lamanya dan suara burung dara.",
            "Obrolan mengenai pengalaman di-bully di masa lalu.",
            "Membahas asal usul gerakan trend \"Kedat-Kedut\" miliknya.",
            "Arthada berbagi pengalaman pertama terjun ke dunia akting/web series.",
            "Alasan Arthada menerima tawaran akting di series \"Sugar Baby\".",
            "Cerita mengharukan tentang keinginan almarhum ayahnya agar ia menjadi penyanyi.",
            "Arthada membahas latar belakang pendidikan agamanya (MI & MTs).",
            "Arthada menunjukkan kemampuannya melantunkan salawat.",
            "Reaksi host terhadap suara merdu Arthada.",
            "Klarifikasi mengenai rumor pindah agama karena foto \"pre-wedding\".",
            "Permainan game \"Dar Dare Dor\" (Truth or Dare).",
            "Arthada menjawab pertanyaan tentang tawaran brand teraneh.",
            "Pertanyaan tentang artis yang terkenal lewat \"jalur orang dalam\".",
            "Arthada memilih antara dunia konten atau akting yang paling toksik.",
            "Membahas impresi pertama orang lain terhadap mereka.",
            "Arthada mengungkapkan tujuan hidupnya di masa depan.",
            "Penutupan acara dan ucapan terima kasih.",
            "Credit title video.",
        ],
        "Catatan": [
            "\"Ilahilas tulil firdausi...\"",
            "Musik latar ceria dan teks \"Slay & Say\".",
            "\"Welcome back to Slay and Say! Bintang tamunya... Arthada!\"",
            "\"Kenalin nama lu dengan gaya lo itu, yang cepet.\"",
            "\"Nama gue Daffa Arthada Gusti Siombing... sekarang sebulan dapat empat digit.\"",
            "\"Sombong yang bisa diterima itu sombongnya lo.\"",
            "\"Kenapa gue bisa ngomong cepet? Gue orang Betawi-Sunda, tapi bokap gue Batak.\"",
            "\"Ayamnya tuh pekok-pekok... gue harus ngomong selesai sebelum ayamnya bunyi.\"",
            "\"Awalnya gara-gara terburu-buru mengejar waktu sebelum si ayam sialan itu.\"",
            "\"Orang-orang yang di titik kayak gue pasti pernah dibully.\"",
            "\"Sebenarnya ada orang bule yang bikin video kedat-kedut, gue ikutin.\"",
            "\"Gimana rasanya sekarang lu udah main di web series?\"",
            "\"Kenapa gue terima? Karena pemainnya udah senior-senior.\"",
            "\"Bokap gue pengen gue kayak Tantri Kotak... pas di IGD dia minta gue nyanyi.\"",
            "\"Gue tuh jago banget selawatan, basic agama gue udah kental.\"",
            "Lantunan lagu religi/salawat oleh Arthada.",
            "\"Gue nggak nyangka loh di balik seorang Arthada gitu...\"",
            "\"Netizen Indonesia itu tolol otaknya... gue cuma foto nemenin Andrew di Bali.\"",
            "\"Kita bakal main game namanya Dar Dare Dor!\"",
            "\"Tawaran brand teraneh? Disuruh ke tukang ayam sama tukang seblak.\"",
            "\"Siapa artis yang menurut lo terkenal dari jalur orang dalem?\"",
            "\"Di antara dunia konten dan dunia akting, mana yang paling toxic?\"",
            "\"Apa first impression terburuk yang pernah lo dapet?\"",
            "\"Goals hidup aku... pengen meratukan keluarga aku.\"",
            "\"Arthada makasih ya udah datang ke Slay and Say!\"",
            "Daftar kru produksi Everest Media.",
        ],
        })
    st.markdown(
    f'<div class="timeline-table-wrapper">{default_timeline.to_html(index=False, escape=False, classes="timeline-table")}</div>',
    unsafe_allow_html=True,
)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Evaluasi Framework ABCD")
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("""
        <div class="insight-box" style="border-left-color: #4F46E5;">
            <b>Attention — Apakah 3 detik pertama menarik perhatian?</b><br><br>
            Video dibuka dengan Arthada menyanyikan salawat, bukan konten komedi/viral seperti biasa dikenal dari dirinya. Pembukaan ini justru jadi hook yang kontras dan mengejutkan karena tidak sesuai ekspektasi penonton terhadap image "sombong cepat ngomong" yang selama ini melekat, sehingga cukup efektif menahan penonton untuk terus menonton.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box" style="border-left-color: #22C55E;">
            <b>Branding — Seberapa jelas & konsisten brand ditampilkan?</b><br><br>
            Branding program "Slay & Say" ditampilkan lewat intro animasi di detik ke-18 dan identitas visual (nama program, host Mochamado) konsisten muncul di sepanjang video. Namun branding brand Arthada sendiri lebih terbangun lewat personal storytelling (ciri khas bicara cepat, gaya "sombong") ketimbang elemen visual/logo formal.
        </div>
        """, unsafe_allow_html=True)
    with a2:
        st.markdown("""
        <div class="insight-box" style="border-left-color: #0EA5E9;">
            <b>Connection — Apakah video membangun koneksi emosional?</b><br><br>
            Ya, cukup kuat. Ada momen personal yang emosional (cerita ayah yang minta dinyanyikan lagu saat di IGD), cerita masa lalu di-bully, serta klarifikasi rumor pindah agama yang membuat penonton melihat sisi vulnerable Arthada di balik citra publiknya yang "sombong". Ini membangun simpati dan hubungan emosional yang lebih dalam dengan audiens.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-box" style="border-left-color: #F97316;">
            <b>Direction — Apakah CTA jelas & mengarahkan aksi?</b><br><br>
            CTA di video ini cenderung lemah/implisit — tidak ada ajakan eksplisit untuk follow, subscribe, atau action tertentu di akhir video. Penutupan hanya berupa ucapan terima kasih dan credit title, sehingga dari sisi konversi/direction framework ABCD, bagian ini jadi titik lemah dibanding 3 elemen lainnya.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Screenshot Adegan Kunci")
    st.caption("Tempel link Google Drive (pastikan sharing diatur 'Anyone with the link') untuk menampilkan gambar.")
    drive_link = st.text_input("Link gambar Google Drive (opsional)")
    if drive_link:
        try:
            file_id = drive_link.split("/d/")[1].split("/")[0]
            direct_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            st.image(direct_url, caption="Key Scene Screenshot", width=500)
        except Exception:
            st.warning("Format link Google Drive tidak dikenali. Gunakan format: https://drive.google.com/file/d/FILE_ID/view")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TAB 3 — CONCLUSION & RECOMMENDATION
# -------------------------------------------------------------------------
with tab3:
    render_header(len(df), brand_a, brand_b)

    st.markdown('<div class="section-title">Kesimpulan Bisnis & Rekomendasi Strategis</div>', unsafe_allow_html=True)

    st.markdown(f'<span class="winner-badge">{leading_brand} unggul dalam total engagement</span>', unsafe_allow_html=True)

    losing_brand = brand_b if leading_brand == brand_a else brand_a

    summary_stats = df.groupby("Brand").agg(
        Total_Engagement=("Engagements", "sum"),
        Rata_rata_Engagement=("Engagements", "mean"),
        Jumlah_Post=("Engagements", "count"),
    ).reset_index()

    # Format angka biar rapi sebelum ditampilkan
    summary_display = summary_stats.copy()
    summary_display["Total_Engagement"] = summary_display["Total_Engagement"].map("{:,.0f}".format)
    summary_display["Rata_rata_Engagement"] = summary_display["Rata_rata_Engagement"].map("{:,.0f}".format)

    st.markdown(
        f'<div class="timeline-table-wrapper">{summary_display.to_html(index=False, escape=False, classes="timeline-table")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### AI-Generated Business Conclusion")
    conclusion_prompt = f"""
    Data ringkasan performa dua brand yang bersaing:
    {summary_stats.to_string(index=False)}

    Brand unggul (berdasarkan total engagement): {leading_brand}
    Brand tertinggal: {losing_brand}

    Sebagai Media Intelligence Analyst, tuliskan:
    1. Kesimpulan bisnis singkat (2-3 kalimat): brand mana yang punya strategi digital lebih baik dan mengapa.
    2. TEPAT 3 rekomendasi strategis (actionable, berbasis data) untuk brand '{losing_brand}' agar dapat memperbaiki kampanye digitalnya.
    Gunakan format bullet point yang rapi.
    """
    default_conclusion = f"""
    <b>Kesimpulan Bisnis:</b><br>
    {leading_brand} unggul dalam total engagement, tetapi rasio rata-rata terhadap median engagement-nya jauh lebih tinggi (6,4x) dibanding {losing_brand} (3,5x) — artinya performa {leading_brand} sangat bergantung pada segelintir post yang viral, bukan konsistensi dari seluruh kontennya. Sebaliknya, {losing_brand} menunjukkan distribusi engagement yang lebih merata dan tercatat nol post bersentimen negatif, meski volume totalnya lebih kecil. Sentimen negatif {leading_brand} juga bukan berasal dari gaya komunikasinya secara umum, melainkan dari pilihan konten spesifik yang berisiko (endorsement yang diboikot, kontroversi busana/agama, kritik peran di series tertentu).
    <br><br>
    <b>Rekomendasi Strategis untuk {losing_brand}:</b>
    <ul>
        <li><b>Jangan kejar volume viral {leading_brand} secara membabi buta.</b> Keunggulan total engagement {leading_brand} didorong segelintir post yang meledak, bukan performa konsisten — mengejar angka ini lewat replikasi gaya yang sama berisiko tinggi tanpa jaminan hasil. Lebih rasional membangun engagement yang stabil dan bisa diprediksi.</li>
        <li><b>Perbesar porsi format yang sudah terbukti unggul, bukan sekadar posting lebih banyak.</b> Data menunjukkan salah satu format konten {losing_brand} justru menghasilkan rata-rata engagement lebih tinggi dari format utamanya sendiri, meski porsinya masih kecil — sinyal konkret bahwa format ini undervalued dan layak diperbesar.</li>
        <li><b>Kelola risiko konten secara spesifik, bukan sekadar "hindari kontroversi" secara umum.</b> Sentimen negatif {leading_brand} berasal dari pilihan konten yang jelas, bukan dari kepribadian brand-nya. {losing_brand} tidak perlu mengubah karakter brand untuk tetap aman — cukup terapkan proses screening sebelum menerima endorsement/proyek berisiko, dan tetap sadar bahwa rekam jejak bebas sentimen negatif saat ini masih berbasis sampel data yang kecil.</li>
    </ul>
    """
    insight_section("conclusion", conclusion_prompt, api_key, model, default_text=default_conclusion)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Catatan Manual Tambahan")
    st.text_area("Tambahkan kesimpulan / rekomendasi manual dari tim analis (opsional)", height=140, key="manual_notes")

    st.markdown('</div>', unsafe_allow_html=True)
