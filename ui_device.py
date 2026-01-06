import streamlit as st
from queries import find_devices
from devices import Device


if "device_status" not in st.session_state:
    st.session_state.device_status = {}
# Eine Überschrift der ersten Ebene
st.write("# Gerätemanagement")

# Eine Überschrift der zweiten Ebene
st.write("## Geräteauswahl")

# Eine Auswahlbox mit Datenbankabfrage, das Ergebnis wird in current_device gespeichert
devices_in_db = find_devices()

devices_in_db = find_devices()

if devices_in_db:
    device_names = [d.get("name") for d in devices_in_db if isinstance(d, dict) and d.get("name")]
    current_device_name = st.selectbox(
        "Gerät auswählen",
        options=device_names,
        key="sbDevice"
    )


    if current_device_name in device_names:
        loaded_device = next((d for d in devices_in_db if d.get("name") == current_device_name), None)

        if loaded_device:
            st.write(f"Loaded Device: {current_device_name}")
        else:
            st.error("Device not found in the database.")
            st.stop()

        with st.form("Device"):
            st.write(loaded_device.get("name"))

            text_input_val = st.text_input("Geräte-Verantwortlicher", value=loaded_device.get("managed_by_user_id", ""))
            loaded_device.set_managed_by_user_id(text_input_val)

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                loaded_device.store_data()
                st.write("Data stored.")
                st.rerun()
    else:
        st.error("Selected device is not in the database.")
else:
    st.write("No devices found.")
    st.stop()

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

#st.write("Session State:")
#st.session_state

def init_ui_state():
    if "device_status" not in st.session_state:
        st.session_state.device_status = {}
