import streamlit as st
import ui_device
import ui_reservations

st.set_page_config(page_title="Case Study 1")

st.title("Case Study 1")
st.write("Grundgerüst: UI -> Logik -> Datenbank (JSON)")

seite = st.sidebar.selectbox("Navigation", ["Devices", "Reservierungen"])

if seite == "Devices":
    pass
elif seite == "Reservierungen":
    ui_reservations.render()


