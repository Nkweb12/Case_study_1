import streamlit as st
from datetime import datetime, date, time

from queries import get_devices, get_users, insert_reservation, list_reservations


def _combine(d: date, t: time) -> datetime:
    """Datum und Uhrzeit zu datetime kombinieren"""
    return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)


def _overlaps(a_start: datetime, a_end: datetime,
              b_start: datetime, b_end: datetime) -> bool:
    
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


    user_name_by_id = {
        u.get("id"): u.get("name", u.get("id"))
        for u in users
        if isinstance(u, dict)
    }


    if not devices:
        st.error("Keine Geräte in der Datenbank vorhanden.")
        st.stop()

    if not users:
        st.error("Keine Benutzer in der Datenbank vorhanden.")
        st.stop()

    device_names = [
        d.get("name")
        for d in devices
        if isinstance(d, dict) and d.get("name")
    ]

    user_options = {
        f'{u.get("name")} ({u.get("id")})': u.get("id")
        for u in users
        if u.get("id")
    }

    st.write("## Neue Reservierung")

    with st.form("reservation_form", clear_on_submit=False):
        device_name = st.selectbox(
            "Gerät auswählen",
            device_names,
            key="res_device"
        )

        user_label = st.selectbox(
            "Benutzer auswählen",
            list(user_options.keys()),
            key="res_user"
        )
        user_id = user_options[user_label]

        col1, col2 = st.columns(2)

        with col1:
            date_from = st.date_input(
                "Datum von",
                value=date.today(),
                key="res_date_from"
            )
            time_from = st.time_input(
                "Uhrzeit von",
                value=time(9, 0),
                key="res_time_from"
            )

        with col2:
            date_to = st.date_input(
                "Datum bis",
                value=date.today(),
                key="res_date_to"
            )
            time_to = st.time_input(
                "Uhrzeit bis",
                value=time(10, 0),
                key="res_time_to"
            )

        submit = st.form_submit_button("Reservieren")

    if submit:
        start_dt = _combine(date_from, time_from)
        end_dt = _combine(date_to, time_to)

        
        if end_dt <= start_dt:
            st.error("Fehler: Endzeit muss nach der Startzeit liegen.")
            st.stop()

        # keine Überschneidung für dasselbe Gerät
        for r in reservations:
            if not isinstance(r, dict):
                continue

            if r.get("device_name") != device_name:
                continue

            try:
                existing_start = datetime.fromisoformat(r.get("start"))
                existing_end = datetime.fromisoformat(r.get("end"))
            except Exception:
                continue

            if _overlaps(start_dt, end_dt, existing_start, existing_end):
                st.error(
                    f"Das Gerät '{device_name}' ist bereits reserviert "
                    f"({existing_start} – {existing_end})."
                )
                st.stop()

        new_reservation = {
            "device_name": device_name,
            "user_id": user_id,
            "start": start_dt.isoformat(timespec="minutes"),
            "end": end_dt.isoformat(timespec="minutes"),
        }

        insert_reservation(new_reservation)
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
        rows.append({
            "Gerät": r.get("device_name", ""),
            "Benutzer": user_name_by_id.get(r.get("user_id"), r.get("user_id")),
            "Von": r.get("start", ""),
            "Bis": r.get("end", ""),
        })

    st.table(rows)


