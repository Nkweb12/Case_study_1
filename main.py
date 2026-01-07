import streamlit as st
import ui_device
import ui_reservations
import ui_users

st.set_page_config(page_title="Case Study 1", layout="wide")

st.title("Case Study 1")
st.write("Grundgerüst: UI → Logik → Datenbank (JSON)")

seite = st.sidebar.selectbox(
    "Navigation",
    ["Devices", "Reservierungen", "Nutzer"]
)

if seite == "Devices":
    ui_device.render()
elif seite == "Reservierungen":
    ui_reservations.render()
else:
    ui_users.render()