import streamlit as st
from queries import find_devices, update_device


def render():
    # session state init for simple status buttons (optional UI state)
    if "device_status" not in st.session_state:
        st.session_state.device_status = {}

    st.write("# Gerätemanagement")
    st.write("## Geräteauswahl")

    devices = find_devices()  # List[dict]
    if not devices:
        st.error("Keine Geräte in der Datenbank vorhanden.")
        st.stop()

    # Build label -> id mapping (always store ID as string)
    id_by_label = {}
    for d in devices:
        if not isinstance(d, dict):
            continue
        did = d.get("id")
        if did is None:
            continue
        did = str(did)
        dn = d.get("device_name") or f"(ohne Name)"
        label = f"{dn} (ID {did})"
        id_by_label[label] = did

    labels = list(id_by_label.keys())
    if not labels:
        st.error("Devices exist, but none has a valid ID / device_name.")
        st.stop()

    current_label = st.selectbox("Gerät auswählen", options=labels, key="sbDevice")
    device_id = id_by_label[current_label]  # string

    # Find selected device dict (compare IDs as string)
    loaded = next((d for d in devices if isinstance(d, dict) and str(d.get("id")) == device_id), None)
    if not loaded:
        st.error("Gerät wurde nicht gefunden.")
        st.stop()

    st.write(f"Loaded Device: {loaded.get('device_name')} (ID {device_id})")

    with st.form("device_form", clear_on_submit=False):
        st.write(loaded.get("device_name", ""))

        managed_val = st.text_input(
            "Geräte-Verantwortlicher (User-ID / E-Mail)",
            value=loaded.get("managed_by_user_id", "")
        )
        active_val = st.checkbox(
            "Aktiv",
            value=bool(loaded.get("is_active", True))
        )

        submitted = st.form_submit_button("Speichern")
        if submitted:
            update_device(
                device_id=device_id,
                managed_by_user_id=managed_val.strip(),
                is_active=active_val
            )
            st.success("Gespeichert.")
            st.rerun()

    # Optional status buttons (UI-only, not stored in DB)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Frei"):
            st.session_state.device_status[device_id] = "frei"
    with col2:
        if st.button("Besetzt"):
            st.session_state.device_status[device_id] = "besetzt"
    with col3:
        if st.button("Wartung"):
            st.session_state.device_status[device_id] = "wartung"

    if device_id not in st.session_state.device_status:
        st.session_state.device_status[device_id] = "frei"

    st.info(f"Status (nur UI): {st.session_state.device_status[device_id]}")
