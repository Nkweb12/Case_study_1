import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).parent / "database.json"


# -----------------------------
# low-level DB helpers
# -----------------------------
def _save_db(db: dict) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")


def _normalize_db(db: Any) -> dict:
    """
    Ensures DB structure:
    {
      "users": { "<user_id>": {"name": "..."} , ... },
      "devices": { "<device_id>": {"device_name": "...", "managed_by_user_id": "...", "is_active": true}, ... },
      "reservations": [ {"device_id": "...", "user_id": "...", "start": "...", "end": "..."}, ... ]
    }

    Also converts older formats if needed:
    - users: list[{"id": "...", "name": "..."}] -> dict
    - devices: list[{"id": "...", "name"/"device_name": "..."}] -> dict
    - reservations: keeps list, but tolerates older keys
    """
    if not isinstance(db, dict):
        db = {}

    db.setdefault("users", {})
    db.setdefault("devices", {})
    db.setdefault("reservations", [])

    # --- users: list -> dict
    if isinstance(db["users"], list):
        new_users: Dict[str, dict] = {}
        for u in db["users"]:
            if isinstance(u, dict) and u.get("id"):
                uid = str(u["id"])
                new_users[uid] = {"name": u.get("name", uid)}
        db["users"] = new_users

    # --- devices: list -> dict
    if isinstance(db["devices"], list):
        new_devices: Dict[str, dict] = {}
        for d in db["devices"]:
            if not isinstance(d, dict):
                continue
            did = d.get("id")
            if not did:
                continue
            did = str(did)
            dn = d.get("device_name") or d.get("name") or did
            new_devices[did] = {
                "device_name": dn,
                "managed_by_user_id": d.get("managed_by_user_id", ""),
                "is_active": bool(d.get("is_active", True)),
            }
        db["devices"] = new_devices

    # --- reservations: ensure list
    if not isinstance(db["reservations"], list):
        db["reservations"] = []

    return db


def _load_db() -> dict:
    if not DB_PATH.exists():
        db = {"users": {}, "devices": {}, "reservations": []}
        _save_db(db)
        return db

    try:
        raw = json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        raw = {"users": {}, "devices": {}, "reservations": []}

    db = _normalize_db(raw)
    # optional: auto-save if structure was fixed
    _save_db(db)
    return db


# -----------------------------
# USERS
# -----------------------------
def get_users() -> List[dict]:
    """
    Returns list:
      [{"id": "<user_id>", "name": "<name>"}]
    """
    db = _load_db()
    users = db.get("users", {})
    out: List[dict] = []
    if isinstance(users, dict):
        for uid, u in users.items():
            if isinstance(u, dict):
                out.append({"id": str(uid), "name": u.get("name", str(uid))})
    return out


# -----------------------------
# DEVICES
# -----------------------------
def find_devices() -> List[dict]:
    """
    Returns list:
      [{"id": "1", "device_name": "...", "managed_by_user_id": "...", "is_active": True}, ...]
    """
    db = _load_db()
    devices = db.get("devices", {})
    out: List[dict] = []

    if isinstance(devices, dict):
        for did, d in devices.items():
            if not isinstance(d, dict):
                continue
            out.append({
                "id": str(did),
                "device_name": d.get("device_name", str(did)),
                "managed_by_user_id": d.get("managed_by_user_id", ""),
                "is_active": bool(d.get("is_active", True)),
            })
    return out


def get_devices() -> List[dict]:
    # alias for other files (ui_reservations.py etc.)
    return find_devices()


def update_device(device_id: str, managed_by_user_id: Optional[str] = None, is_active: Optional[bool] = None) -> bool:
    """
    Updates device in DB. Returns True if updated, False if not found.
    """
    db = _load_db()
    devices = db.get("devices", {})
    device_id = str(device_id)

    if not isinstance(devices, dict) or device_id not in devices or not isinstance(devices[device_id], dict):
        return False

    if managed_by_user_id is not None:
        devices[device_id]["managed_by_user_id"] = managed_by_user_id

    if is_active is not None:
        devices[device_id]["is_active"] = bool(is_active)

    db["devices"] = devices
    _save_db(db)
    return True


def set_device_active(device_id: str, is_active: bool) -> bool:
    # helper if kdo uporablja to ime
    return update_device(device_id, is_active=is_active)


# -----------------------------
# RESERVATIONS
# -----------------------------
def list_reservations() -> List[dict]:
    """
    Returns list of reservations.
    Expected reservation format:
      {"device_id": "1", "user_id": "admin@mci.edu", "start": "YYYY-MM-DDTHH:MM", "end": "YYYY-MM-DDTHH:MM"}
    But also tolerates older:
      {"device_name": "...", "user_id": "...", "start": "...", "end": "..."}
    """
    db = _load_db()
    res = db.get("reservations", [])
    if not isinstance(res, list):
        return []
    # keep only dicts
    return [r for r in res if isinstance(r, dict)]


def insert_reservation(reservation: dict) -> None:
    """
    Appends reservation dict to DB.
    """
    db = _load_db()
    res_list = db.get("reservations", [])
    if not isinstance(res_list, list):
        res_list = []

    if isinstance(reservation, dict):
        res_list.append(reservation)

    db["reservations"] = res_list
    _save_db(db)
