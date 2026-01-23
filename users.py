import os
from tinydb import TinyDB, Query
from serializer import serializer

class User:

    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json"), storage=serializer).table("users")

    def __init__(self, id, name) -> None:
        """Create a new user based on the given name and id"""
        self.name = name
        self.id = id

    def store_data(self)-> None:
        UserQuery = Query()
        result = self.db_connector.search(UserQuery.id == self.id)

        if result:
            self.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])

        else:
            self.db_connector.insert(self.__dict__)

        

    def delete(self) -> None:
        UserQuery = Query()
        self.db_connector.remove(UserQuery.id == self.id)
    
    def __str__(self):
        return f"User {self.id} - {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def find_all(cls) -> list:
        users = []
        for user_data in User.db_connector.all():
            users.append(User(user_data["id"], user_data["name"]))
        return users

    @classmethod
    def find_by_attribute(cls, by_attribute : str, attribute_value : str) -> 'User':
        UserQuery = Query()
        result = cls.db_connector.search(UserQuery[by_attribute] == attribute_value)
        if result:
            user_data = result[0]
            return User(user_data["id"], user_data["name"])
        else:
            return None
