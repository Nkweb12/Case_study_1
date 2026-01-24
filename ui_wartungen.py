import streamlit as st
from datetime import date, datetime

from devices import Device
from wartungen import MaintenanceManager

st.title("🛠 Wartungsmanagement")

# ---------- Device selection ----------
devices = Device.find_all()
device_ids = [d.id for d in devices]

selected_device_id = st.selectbox("Gerät auswählen", device_ids)
device = next(d for d in devices if d.id == selected_device_id)

# ---------- Load or create maintenance ----------
maintenance = MaintenanceManager.find_by_attribute(
    "device_id", device.id
)

if maintenance is None:
    maintenance = MaintenanceManager(
        id=device.id,
        device_id=device.id
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

# ---------- Save ----------
if st.button("Speichern"):
    maintenance.first_maintenance = datetime.combine(fm, datetime.min.time())
    maintenance.maintenance_interval_days = interval
    maintenance.maintenance_cost = cost
    maintenance.end_of_life = datetime.combine(eol, datetime.min.time())

    maintenance.store_data()
    st.success("Gespeichert")

# ---------- Next maintenance ----------
next_date = MaintenanceManager.get_next_maintenance_date(maintenance)
if next_date:
    st.success(f"Nächste Wartung: {next_date.date()}")

# ---------- Quarter costs ----------
st.subheader("Quartalskosten")
st.write(f"{MaintenanceManager.calculate_cost_for_quarter():.2f} €")
