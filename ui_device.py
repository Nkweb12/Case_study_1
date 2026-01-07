from operator import add
import streamlit as st
from queries import find_devices, update_device, add_device, delete_device, get_users


def render():
    # session state init for simple status buttons (optional UI state)
    if "device_status" not in st.session_state:
        st.session_state.device_status = {}
    users = get_users()
    user_options = {u["name"] + f' ({u["id"]})': u["id"] for u in users}

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

        current_manager = loaded.get("managed_by_user_id", "")

        labels = list(user_options.keys())
        values = list(user_options.values())

        if current_manager in values:
            index = values.index(current_manager)
        else:
            index = 0

        managed_val = st.selectbox(
            "Geräte-Verantwortlicher",
            options=labels,
            index=index
        )
        managed_user_id = user_options[managed_val]

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

    st.write("## Gerät löschen")
    
    if st.button("❌ Gerät endgültig löschen"):
        delete_device(device_id)
        st.warning("Gerät gelöscht.")
        st.rerun()

    st.write("## Neues Gerät")

    with st.form("add_device_form"):
        new_name = st.text_input("Gerätename")
        new_manager = st.text_input("Verantwortlicher (User-ID)")
        add = st.form_submit_button("Gerät anlegen")

    if add:
        if not new_name:
            st.error("Gerätename fehlt.")
        else:
            add_device(new_name.strip(), new_manager.strip())
            st.success("Gerät hinzugefügt.")
            st.rerun()

