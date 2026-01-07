import streamlit as st
from datetime import datetime, date, time

from queries import get_devices, get_users, insert_reservation, list_reservations


def _combine(d: date, t: time) -> datetime:
    """Datum und Uhrzeit zu datetime kombinieren"""
    return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second)


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def _normalize_devices(devices_raw):
    """
    Expected output: list of dicts with keys:
    - id (string)
    - device_name (string)
    - managed_by_user_id (string optional)
    - is_active (bool optional)
    """
    devices = []

    if isinstance(devices_raw, dict):
        # dict form: {"1": {...}, "2": {...}}
        for k, v in devices_raw.items():
            if isinstance(v, dict):
                d = {"id": str(k), **v}
                devices.append(d)

    elif isinstance(devices_raw, list):
        # list form already
        for v in devices_raw:
            if isinstance(v, dict):
                if "id" in v:
                    v["id"] = str(v["id"])
                devices.append(v)

    # ensure required keys
    for d in devices:
        if "id" not in d and d.get("device_id"):
            d["id"] = str(d["device_id"])
        # map legacy name -> device_name
        if "device_name" not in d and d.get("name"):
            d["device_name"] = d.get("name")

    return devices


def _normalize_users(users_raw):
    """
    Expected output: list of dicts with keys:
    - id (string)
    - name (string)
    """
    users = []

    if isinstance(users_raw, dict):
        # dict form: {"admin@mci.edu": {"name": "Admin"}, ...}
        for k, v in users_raw.items():
            if isinstance(v, dict):
                users.append({"id": str(k), "name": v.get("name", str(k))})
            else:
                users.append({"id": str(k), "name": str(k)})

    elif isinstance(users_raw, list):
        for u in users_raw:
            if isinstance(u, dict):
                if "id" in u:
                    u["id"] = str(u["id"])
                users.append(u)

    # ensure keys
    for u in users:
        if "id" not in u and u.get("user_id"):
            u["id"] = str(u["user_id"])
        if "name" not in u:
            u["name"] = u.get("id", "")

    return users


def render():
    st.write("# Reservierungssystem")

    # --- load + normalize ---
    devices_raw = get_devices()
    users_raw = get_users()
    reservations = list_reservations()

    devices = _normalize_devices(devices_raw)
    users = _normalize_users(users_raw)

    if not devices:
        st.error("Keine Geräte in der Datenbank vorhanden.")
        st.stop()

    if not users:
        st.error("Keine Benutzer in der Datenbank vorhanden.")
        st.stop()

    # lookups
    device_name_by_id = {
        str(d.get("id")): d.get("device_name", str(d.get("id")))
        for d in devices
        if isinstance(d, dict) and d.get("id")
    }
    user_name_by_id = {
        str(u.get("id")): u.get("name", str(u.get("id")))
        for u in users
        if isinstance(u, dict) and u.get("id")
    }

    # --- options for dropdowns ---
    device_options = {
        f'{d.get("device_name","(ohne Name)")} (ID {d.get("id")})': str(d.get("id"))
        for d in devices
        if isinstance(d, dict) and d.get("id")
    }
    device_labels = list(device_options.keys())
    if not device_labels:
        st.error("Keine Geräte mit gültiger ID/Name gefunden.")
        st.stop()

    user_options = {
        f'{u.get("name", u.get("id"))} ({u.get("id")})': str(u.get("id"))
        for u in users
        if isinstance(u, dict) and u.get("id")
    }
    user_labels = list(user_options.keys())
    if not user_labels:
        st.error("Keine Benutzer mit gültiger ID gefunden.")
        st.stop()

    # --- new reservation form ---
    st.write("## Neue Reservierung")

    with st.form("reservation_form", clear_on_submit=False):
        device_label = st.selectbox("Gerät auswählen", device_labels, key="res_device")
        device_id = device_options[device_label]

        user_label = st.selectbox("Benutzer auswählen", user_labels, key="res_user")
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

        # overlap check for the same device
        for r in reservations:
            if not isinstance(r, dict):
                continue

            # new structure uses device_id
            if r.get("device_id") is not None:
                if str(r.get("device_id")) != str(device_id):
                    continue
            # legacy structure might use device_name
            elif r.get("device_name") is not None:
                # compare by name (best effort)
                selected_name = device_name_by_id.get(str(device_id), str(device_id))
                if str(r.get("device_name")) != str(selected_name):
                    continue
            else:
                continue

            try:
                existing_start = datetime.fromisoformat(r.get("start"))
                existing_end = datetime.fromisoformat(r.get("end"))
            except Exception:
                continue

            if _overlaps(start_dt, end_dt, existing_start, existing_end):
                dn = device_name_by_id.get(str(device_id), str(device_id))
                st.error(
                    f"Das Gerät '{dn}' ist bereits reserviert "
                    f"({existing_start} - {existing_end})."
                )
                st.stop()

        # save NEW reservation format
        new_res = {
            "device_id": str(device_id),
            "user_id": str(user_id),
            "start": start_dt.isoformat(timespec="minutes"),
            "end": end_dt.isoformat(timespec="minutes"),
        }
        insert_reservation(new_res)
        st.success("Reservierung erfolgreich gespeichert.")
        st.rerun()

    # --- existing reservations ---
    st.write("## Bestehende Reservierungen")

    if not reservations:
        st.info("Es sind noch keine Reservierungen vorhanden.")
        return

    rows = []
    for r in reservations:
        if not isinstance(r, dict):
            continue

        # device label (support both new + legacy)
        if r.get("device_id") is not None:
            dev = device_name_by_id.get(str(r.get("device_id")), str(r.get("device_id")))
        else:
            dev = r.get("device_name", "")

        # user label
        uid = r.get("user_id", "")
        usr = user_name_by_id.get(str(uid), str(uid))

        rows.append({
            "Gerät": dev,
            "Benutzer": usr,
            "Von": r.get("start", ""),
            "Bis": r.get("end", ""),
        })

    st.table(rows)
