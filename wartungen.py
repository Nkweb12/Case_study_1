from datetime import datetime, timedelta
from typing import Self

from serializable import Serializable
from database_inheritance import DatabaseConnector
from devices import Device


class MaintenanceManager(Serializable):
    """
    Represents maintenance data for ONE device
    """

    db_connector = DatabaseConnector().get_table("maintenances")

    def __init__(
        self,
        id: str,                 # same as device.id
        device_id: str,
        first_maintenance: datetime = None,
        maintenance_interval_days: int = None,
        maintenance_cost: float = 0.0,
        end_of_life: datetime = None,
        creation_date: datetime = None,
        last_update: datetime = None,
    ):
        super().__init__(id, creation_date, last_update)

        self.device_id = device_id
        self.first_maintenance = first_maintenance
        self.maintenance_interval_days = maintenance_interval_days
        self.maintenance_cost = maintenance_cost
        self.end_of_life = end_of_life

    # ---------- Serializable ----------
    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            device_id=data["device_id"],
            first_maintenance=data.get("first_maintenance"),
            maintenance_interval_days=data.get("maintenance_interval_days"),
            maintenance_cost=data.get("maintenance_cost", 0.0),
            end_of_life=data.get("end_of_life"),
            creation_date=data.get("creation_date"),
            last_update=data.get("last_update"),
        )

    def __str__(self):
        return f"Maintenance for device {self.device_id}"

    # ---------- Logic ----------
    @staticmethod
    def get_next_maintenance_date(maintenance: "MaintenanceManager"):
        if not maintenance.first_maintenance or not maintenance.maintenance_interval_days:
            return None

        today = datetime.now()
        next_date = maintenance.first_maintenance

        while next_date < today:
            next_date += timedelta(days=maintenance.maintenance_interval_days)

        if maintenance.end_of_life and next_date > maintenance.end_of_life:
            return None

        return next_date
 
    @staticmethod
    def get_quarter_bounds(date: datetime):
        y, m = date.year, date.month
        if m <= 3:
            return datetime(y, 1, 1), datetime(y, 3, 31, 23, 59, 59)
        elif m <= 6:
            return datetime(y, 4, 1), datetime(y, 6, 30, 23, 59, 59)
        elif m <= 9:
            return datetime(y, 7, 1), datetime(y, 9, 30, 23, 59, 59)
        else:
            return datetime(y, 10, 1), datetime(y, 12, 31, 23, 59, 59)

    @staticmethod
    def calculate_cost_for_quarter():
        today = datetime.now()
        q_start, q_end = MaintenanceManager.get_quarter_bounds(today)

        total = 0.0
        for m in MaintenanceManager.find_all():
            if not m.first_maintenance or not m.maintenance_interval_days:
                continue

            d = m.first_maintenance
            while d <= q_end:
                if q_start <= d <= q_end:
                    total += m.maintenance_cost
                d += timedelta(days=m.maintenance_interval_days)

        return total
