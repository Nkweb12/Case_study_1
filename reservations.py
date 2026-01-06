import uuid
from datetime import date
import queries


class Reservation:
    def __init__(self, reservation_id, device_id, user_email, start_date, end_date):
        self.reservation_id = reservation_id
        self.device_id = device_id
        self.user_email = user_email
        self.start_date = start_date  
        self.end_date = end_date      


def _overlaps(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    return start_a < end_b and start_b < end_a


def is_device_available(device_id: str, start_date: date, end_date: date) -> bool:
    reservations = queries.list_reservations()

    for r in reservations:
        if r.get("device_id") != device_id:
            continue

        existing_start = date.fromisoformat(r["start_date"])
        existing_end = date.fromisoformat(r["end_date"])

        if _overlaps(start_date, end_date, existing_start, existing_end):
            return False

    return True


def create_reservation(device_id, user_email, start_date: date, end_date: date):
    if start_date >= end_date:
        raise ValueError("Startdatum muss vor dem Enddatum liegen")

    if not is_device_available(device_id, start_date, end_date):
        raise ValueError("Gerät ist in diesem Zeitraum bereits reserviert")

    reservation = Reservation(
        reservation_id=str(uuid.uuid4()),
        device_id=device_id,
        user_email=user_email,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )

    queries.insert_reservation(reservation.__dict__)
    return reservation


def list_reservations():
    return queries.list_reservations()

