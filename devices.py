from dataclasses import dataclass
import queries

@dataclass
class Device:
    name: str
    managed_by_user_id: str
    is_active: bool = True

    def store(self) -> None:
        queries.add_device(self.name, self.managed_by_user_id, self.is_active)

    def set_active(self, active: bool) -> None:
        self.is_active = active
        queries.set_device_active(self.name, active)

def load_all() -> list[Device]:
    return [Device(**d) for d in queries.get_devices()]
