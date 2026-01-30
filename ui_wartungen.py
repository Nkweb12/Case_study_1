import streamlit as st
from datetime import date, datetime
from queries import find_devices
from wartungen import MaintenanceManager

st.title("🛠 Wartungsmanagement")


def render():
    devices = find_devices()  # List[dict]

    if not devices:
        st.error("Keine Geräte vorhanden.")
        st.stop()

    device_ids = [str(d.get("id")) for d in devices if d.get("id") is not None]

    selected_device_id = st.selectbox("Gerät auswählen", device_ids)

    device = next(
        d for d in devices if str(d.get("id")) == selected_device_id
    )

    try:
        maintenance = MaintenanceManager.find_by_attribute(
            "device_id", selected_device_id
        )
    except Exception as e:
        st.warning("Wartungsdaten konnten nicht geladen werden (defekte Tabelle).")
        maintenance = None

    if maintenance is None:
        maintenance = MaintenanceManager(
            id=str(selected_device_id),
            device_id=str(selected_device_id)
        )

    st.subheader("Wartungsdaten")

    fm = st.date_input(
        "Erste Wartung",
        value=maintenance.first_maintenance.date()
        if maintenance.first_maintenance else date.today()
    )

    interval = st.number_input(
        "Intervall (Tage)",
        min_value=1,
        value=maintenance.maintenance_interval_days or 30
    )

    cost = st.number_input(
        "Kosten pro Wartung (€)",
        min_value=0.0,
        value=maintenance.maintenance_cost
    )

    eol = st.date_input(
        "End of Life",
        value=maintenance.end_of_life.date()
        if maintenance.end_of_life else fm
    )

    if st.button("Speichern"):
        maintenance.first_maintenance = datetime.combine(fm, datetime.min.time())
        maintenance.maintenance_interval_days = interval
        maintenance.maintenance_cost = cost
        maintenance.end_of_life = datetime.combine(eol, datetime.min.time())

        try:
            maintenance.store_data()
            st.success("Gespeichert")
        except Exception:
            st.error("Speichern fehlgeschlagen (defekte Wartungstabelle).")

    try:
        next_date = MaintenanceManager.get_next_maintenance_date(maintenance)
        if next_date:
            st.success(f"Nächste Wartung: {next_date.date()}")
    except Exception:
        pass

    st.subheader("Quartalskosten")
    try:
        st.write(f"{MaintenanceManager.calculate_cost_for_quarter():.2f} €")
    except Exception:
        st.write("Nicht verfügbar (defekte Wartungstabelle).")
