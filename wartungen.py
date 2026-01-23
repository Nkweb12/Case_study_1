from datetime import datetime, timedelta
from devices import Device


class MaintenanceManager:

    @staticmethod
    def get_next_maintenance_date(device):
        today = datetime.now()

        if not device.first_maintenance or not device.maintenance_interval_days:
            return None

        if device.end_of_life and today > device.end_of_life:
            return None

        next_date = device.first_maintenance

        while next_date < today:
            next_date += timedelta(days=device.maintenance_interval_days)

        if device.end_of_life and next_date > device.end_of_life:
            return None

        return next_date
 
    @staticmethod
    def get_quarter_bounds(date):
        y, m = date.year, date.month
        if m <= 3:
            return datetime(y,1,1), datetime(y,3,31,23,59,59)
        elif m <= 6:
            return datetime(y,4,1), datetime(y,6,30,23,59,59)
        elif m <= 9:
            return datetime(y,7,1), datetime(y,9,30,23,59,59)
        else:
            return datetime(y,10,1), datetime(y,12,31,23,59,59)

    @staticmethod
    def calculate_cost_for_quarter():
        today = datetime.now()
        q_start, q_end = MaintenanceManager.get_quarter_bounds(today)

        total = 0.0
        for device in Device.find_all():
            if not device.first_maintenance or not device.maintenance_interval_days:
                continue

            date = device.first_maintenance
            while date <= q_end:
                if q_start <= date <= q_end:
                    total += device.maintenance_cost
                date += timedelta(days=device.maintenance_interval_days)

        return total