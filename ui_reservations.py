import streamlit as st
from datetime import datetime, date, time

from queries import get_devices, get_users, insert_reservation, list_reservations


def _combine(d: date, t: time) -> datetime:
    return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def render():
    st.write("# Reservierungssystem")

    devices = get_devices()
    users = get_users()
    reservations = list_reservations()

    if not devices:
        st.error("Keine Geräte in der Datenbank vorhanden.")
        st.stop()
    if not users:
        st.error("Keine Benutzer in der Datenbank vorhanden.")
        st.stop()

    
    device_name_by_id = {str(d["id"]): d.get("device_name", str(d["id"])) for d in devices if isinstance(d, dict) and d.get("id")}
    user_name_by_id = {str(u["id"]): u.get("name", str(u["id"])) for u in users if isinstance(u, dict) and u.get("id")}

   
    device_options = {f'{device_name_by_id[str(d["id"])]} (ID {d["id"]})': str(d["id"]) for d in devices if d.get("id")}
    user_options = {f'{user_name_by_id[str(u["id"])]} ({u["id"]})': str(u["id"]) for u in users if u.get("id")}

    st.write("## Neue Reservierung")

    with st.form("reservation_form", clear_on_submit=False):
        device_label = st.selectbox("Gerät auswählen", list(device_options.keys()), key="res_device")
        user_label = st.selectbox("Benutzer auswählen", list(user_options.keys()), key="res_user")

        device_id = device_options[device_label]
        user_id = user_options[user_label]

        col1, col2 = st.columns(2)
        with col1:
            date_from = st.date_input("Datum von", value=date.today(), key="res_date_from")
            time_from = st.time_input("Uhrzeit von", value=time(9, 0), key="res_time_from")
        with col2:
            date_to = st.date_input("Datum bis", value=date.today(), key="res_date_to")
            time_to = st.time_input("Uhrzeit bis", value=time(10, 0), key="res_time_to")

        submit = st.form_submit_button("Reservieren")

    if submit:
        start_dt = _combine(date_from, time_from)
        end_dt = _combine(date_to, time_to)

        if end_dt <= start_dt:
            st.error("Fehler: Endzeit muss nach der Startzeit liegen.")
            st.stop()

        
        for r in reservations:
            if not isinstance(r, dict):
                continue
            if str(r.get("device_id", "")) != str(device_id):
                continue
            try:
                existing_start = datetime.fromisoformat(r.get("start"))
                existing_end = datetime.fromisoformat(r.get("end"))
            except Exception:
                continue

            if _overlaps(start_dt, end_dt, existing_start, existing_end):
                dn = device_name_by_id.get(str(device_id), str(device_id))
                st.error(f"Das Gerät '{dn}' ist bereits reserviert ({existing_start} – {existing_end}).")
                st.stop()

        insert_reservation(
            {
                "device_id": str(device_id),
                "user_id": str(user_id),
                "start": start_dt.isoformat(timespec="minutes"),
                "end": end_dt.isoformat(timespec="minutes"),
            }
        )
        st.success("Reservierung erfolgreich gespeichert.")
        st.rerun()

    st.write("## Bestehende Reservierungen")

    reservations = list_reservations()
    if not reservations:
        st.info("Es sind noch keine Reservierungen vorhanden.")
        return

    rows = []
    for r in reservations:
        if not isinstance(r, dict):
            continue
        did = str(r.get("device_id", ""))
        uid = str(r.get("user_id", ""))
        rows.append(
            {
                "Gerät": device_name_by_id.get(did, did),
                "Benutzer": user_name_by_id.get(uid, uid),
                "Von": r.get("start", ""),
                "Bis": r.get("end", ""),
            }
        )

    st.table(rows)
