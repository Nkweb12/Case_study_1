import streamlit as st
from datetime import date
from devices import Device
from wartungen import MaintenanceManager

st.title("🛠 Wartungsmanagement")

devices = Device.find_all()
device_names = [d.device_name for d in devices]

selected = st.selectbox("Gerät auswählen", device_names)
device = next(d for d in devices if d.device_name == selected)

st.subheader("Wartungsdaten")

fm = st.date_input("Erste Wartung", value=device.first_maintenance or date.today())
interval = st.number_input("Intervall (Tage)", min_value=1, value=device.maintenance_interval_days or 30)
cost = st.number_input("Kosten pro Wartung (€)", min_value=0.0, value=device.maintenance_cost)
eol = st.date_input("End of Life", value=device.end_of_life or fm)

if st.button("Speichern"):
    device.set_first_maintenance(datetime.combine(fm, datetime.min.time()))
    device.set_maintenance_interval_days(interval)
    device.set_maintenance_cost(cost)
    device.set_end_of_life(datetime.combine(eol, datetime.min.time()))
    device.store_data()
    st.success("Gespeichert")

next_date = MaintenanceManager.get_next_maintenance_date(device)
if next_date:
    st.success(f"Nächste Wartung: {next_date.date()}")

st.subheader("Quartalskosten")
st.write(f"{MaintenanceManager.calculate_cost_for_quarter():.2f} €")
