import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.json"

def _load_db() -> dict:
    if not DB_PATH.exists():
        return {"users": [], "devices": [], "reservations": []}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))

def _save_db(db: dict) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")

def get_users() -> list[dict]:
    return _load_db().get("users", [])

def get_devices() -> list[dict]:
    return _load_db().get("devices", [])

def add_device(name: str, managed_by_user_id: str, is_active: bool = True) -> None:
    db = _load_db()
    db.setdefault("devices", []).append(
        {"name": name, "managed_by_user_id": managed_by_user_id, "is_active": is_active}
    )
    _save_db(db)

def set_device_active(name: str, is_active: bool) -> None:
    db = _load_db()
    for d in db.get("devices", []):
        if d.get("name") == name:
            d["is_active"] = is_active
    _save_db(db)



def insert_reservation(reservation_dict: dict) -> None:
    db = _load_db()
    db.setdefault("reservations", []).append(reservation_dict)
    _save_db(db)


def list_reservations() -> list[dict]:
    return _load_db().get("reservations", [])

def find_devices() -> list[dict]:
    return get_devices()