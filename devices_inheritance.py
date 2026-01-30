from typing import Self
from datetime import datetime

from serializable import Serializable
from database_inheritance import DatabaseConnector

class Device(Serializable):

    db_connector =  DatabaseConnector().get_table("devices")

    def __init__(self, id: str, managed_by_user_id: str, end_of_life: datetime = None, creation_date: datetime = None, last_update: datetime = None):
        super().__init__(id, creation_date, last_update)
        # The user id of the user that manages the device
        # We don't store the user object itself, but only the id (as a key)
        self.managed_by_user_id = managed_by_user_id
        self.is_active = True
        self.end_of_life = end_of_life if end_of_life else datetime.today().date()
   
    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        return cls(data['id'], data['managed_by_user_id'], data['end_of_life'], data['creation_date'], data['last_update'])

    def __str__(self) -> str:
        return f"Device: {self.id} ({self.managed_by_user_id}) - Active: {self.is_active} - Created: {self.creation_date} - Last Update: {self.last_update}"

    def set_managed_by_user_id(self, managed_by_user_id: str):
        """Expects `managed_by_user_id` to be a valid user id that exists in the database."""
        self.managed_by_user_id = managed_by_user_id

if __name__ == "__main__":
    # Create a device
    device1 = Device("Device1", "one@mci.edu")
    device2 = Device("Device2", "two@mci.edu") 
    device3 = Device("Device3", "two@mci.edu") 
    device1.store_data()
    device2.store_data()
    device3.store_data()
    device4 = Device("Device3", "four@mci.edu") 
    device4.store_data()
    
    loaded_device = Device.find_by_attribute("id", "Device2")
    if loaded_device:
        print(f"Loaded: {loaded_device}")
    else:
        print("Device not found.")

    all_devices = Device.find_all()
    for device in all_devices:
        print(device)