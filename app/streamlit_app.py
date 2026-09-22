"""Streamlit Cloud entry point.

Serves the finished, self-contained page (app/index.html) inside a full-bleed
iframe. The page is pure HTML/JS with the price data and calculation engine
inlined, so this wrapper needs only Streamlit — no plotly, pandas, or fintools.

Rebuild index.html from source with:  node scripts/build_page.mjs
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="¿Puede un IUL triplicar $72,000 en $214,000?",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Strip Streamlit chrome so the embedded page reads as its own site.
st.markdown(
    """
    <style>
      .block-container { padding: 0 !important; max-width: 100% !important; }
      [data-testid="stHeader"], #MainMenu, footer { display: none !important; }
      [data-testid="stAppViewContainer"] { background: transparent; }
    </style>
    """,
    unsafe_allow_html=True,
)

html = (Path(__file__).resolve().parent / "index.html").read_text(encoding="utf-8")
components.html(html, height=3400, scrolling=True)
