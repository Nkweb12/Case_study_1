import streamlit as st
from queries import find_devices, _load_db, _save_db

# session state init
if "device_status" not in st.session_state:
    st.session_state.device_status = {}

st.write("# Gerätemanagement")
st.write("## Geräteauswahl")

devices_in_db = find_devices()  # list[dict]

if not devices_in_db:
    st.error("No devices found.")
    st.stop()


device_names = [d.get("name") for d in devices_in_db if isinstance(d, dict) and d.get("name")]

if not device_names:
    st.error("Devices exist, but none has a valid 'name'.")
    st.stop()

current_device_name = st.selectbox("Gerät auswählen", options=device_names, key="sbDevice")


loaded_device = next((d for d in devices_in_db if d.get("name") == current_device_name), None)

if not loaded_device:
    st.error("Device not found in the database.")
    st.stop()

st.write(f"Loaded Device: {current_device_name}")

with st.form("Device"):
    st.write(loaded_device.get("name", ""))

    text_input_val = st.text_input(
        "Geräte-Verantwortlicher",
        value=loaded_device.get("managed_by_user_id", "")
    )

    submitted = st.form_submit_button("Submit")
    if submitted:
        
        loaded_device["managed_by_user_id"] = text_input_val

        
        db = _load_db()
        devs = db.get("devices", [])

        for d in devs:
            if d.get("name") == current_device_name:
                d["managed_by_user_id"] = text_input_val
                break

        db["devices"] = devs
        _save_db(db)

        st.success("Data stored.")
        st.rerun()

# status 
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Frei"):
        st.session_state.device_status[current_device_name] = "frei"
with col2:
    if st.button("Besetzt"):
        st.session_state.device_status[current_device_name] = "besetzt"
with col3:
    if st.button("Wartung"):
        st.session_state.device_status[current_device_name] = "wartung"

if current_device_name not in st.session_state.device_status:
    st.session_state.device_status[current_device_name] = "frei"

