import streamlit as st
from pages import ingest, assistant

st.set_page_config(
    page_title="RepoSense",
    page_icon="🔍",
    layout="centered"
)

if st.session_state.get("ingested"):
    assistant.render()
else:
    ingest.render()