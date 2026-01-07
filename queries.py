import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).parent / "database.json"



def _save_db(db: dict) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")


def _normalize_db(db: Any) -> dict:
   
    if not isinstance(db, dict):
        db = {}

    users = db.get("users", {})
    devices = db.get("devices", {})
    reservations = db.get("reservations", [])

    
    if isinstance(users, list):
        # convert list -> dict
        new_users: Dict[str, Dict[str, Any]] = {}
        for u in users:
            if not isinstance(u, dict):
                continue
            uid = u.get("id")
            if not uid:
                continue
            new_users[str(uid)] = {"name": u.get("name", str(uid))}
        users = new_users
    elif not isinstance(users, dict):
        users = {}

    
    if isinstance(devices, list):
        # convert list -> dict with numeric ids
        new_devices: Dict[str, Dict[str, Any]] = {}
        i = 1
        for d in devices:
            if not isinstance(d, dict):
                continue
            dev_id = str(d.get("id") or i)
            i += 1
            new_devices[dev_id] = {
                "device_name": d.get("device_name") or d.get("name") or f"Device {dev_id}",
                "managed_by_user_id": d.get("managed_by_user_id", ""),
                "is_active": bool(d.get("is_active", True)),
            }
        devices = new_devices
    elif isinstance(devices, dict):
        # ensure each device has correct keys
        fixed: Dict[str, Dict[str, Any]] = {}
        for dev_id, d in devices.items():
            if not isinstance(d, dict):
                continue
            fixed[str(dev_id)] = {
                "device_name": d.get("device_name") or d.get("name") or f"Device {dev_id}",
                "managed_by_user_id": d.get("managed_by_user_id", ""),
                "is_active": bool(d.get("is_active", True)),
            }
        devices = fixed
    else:
        devices = {}

    
    if not isinstance(reservations, list):
        reservations = []

    # If old reservations used device_name, try map -> device_id
    name_to_id = {v.get("device_name"): k for k, v in devices.items() if isinstance(v, dict)}
    new_res: List[dict] = []
    for r in reservations:
        if not isinstance(r, dict):
            continue

        # if already new
        if r.get("device_id"):
            new_res.append(
                {
                    "device_id": str(r.get("device_id")),
                    "user_id": str(r.get("user_id", "")),
                    "start": r.get("start", ""),
                    "end": r.get("end", ""),
                }
            )
            continue

        
        dev_name = r.get("device_name")
        dev_id = name_to_id.get(dev_name)
        if dev_id:
            new_res.append(
                {
                    "device_id": str(dev_id),
                    "user_id": str(r.get("user_id", "")),
                    "start": r.get("start", ""),
                    "end": r.get("end", ""),
                }
            )

    return {"users": users, "devices": devices, "reservations": new_res}


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
    _save_db(db)  
    return db



def get_users() -> List[dict]:
    db = _load_db()
    users = db.get("users", {})
    out: List[dict] = []
    if isinstance(users, dict):
        for uid, u in users.items():
            if not isinstance(u, dict):
                continue
            out.append({"id": str(uid), "name": u.get("name", str(uid))})
    return out


def get_devices() -> List[dict]:
    db = _load_db()
    devices = db.get("devices", {})
    out: List[dict] = []
    if isinstance(devices, dict):
        for dev_id, d in devices.items():
            if not isinstance(d, dict):
                continue
            out.append(
                {
                    "id": str(dev_id),
                    "device_name": d.get("device_name", str(dev_id)),
                    "managed_by_user_id": d.get("managed_by_user_id", ""),
                    "is_active": bool(d.get("is_active", True)),
                }
            )
    return out



def find_devices() -> List[dict]:
    return get_devices()


def list_reservations() -> List[dict]:
    db = _load_db()
    res = db.get("reservations", [])
    if not isinstance(res, list):
        return []
    out: List[dict] = []
    for r in res:
        if not isinstance(r, dict):
            continue
        out.append(
            {
                "device_id": str(r.get("device_id", "")),
                "user_id": str(r.get("user_id", "")),
                "start": r.get("start", ""),
                "end": r.get("end", ""),
            }
        )
    return out


def insert_reservation(new_res: dict) -> None:
    db = _load_db()
    res = db.get("reservations", [])
    if not isinstance(res, list):
        res = []

    res.append(
        {
            "device_id": str(new_res.get("device_id", "")),
            "user_id": str(new_res.get("user_id", "")),
            "start": str(new_res.get("start", "")),
            "end": str(new_res.get("end", "")),
        }
    )
    db["reservations"] = res
    _save_db(db)


def update_device(device_id: str, managed_by_user_id: Optional[str] = None, is_active: Optional[bool] = None) -> None:
    db = _load_db()
    devs = db.get("devices", {})
    if not isinstance(devs, dict):
        devs = {}

    did = str(device_id)
    if did not in devs or not isinstance(devs[did], dict):
        devs[did] = {"device_name": f"Device {did}", "managed_by_user_id": "", "is_active": True}

    if managed_by_user_id is not None:
        devs[did]["managed_by_user_id"] = managed_by_user_id
    if is_active is not None:
        devs[did]["is_active"] = bool(is_active)

    db["devices"] = devs
    _save_db(db)
