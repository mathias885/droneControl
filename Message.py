from enum import Enum
import json

# Definizione dell'enumerazione Command
class Command(Enum):
    FLY_UP = "meters"
    TRANSLATE = "coordinates"
    LAND_AT = "mosca"
    LAND = "none"
    QUIT = "quit"

class Message:
    def __init__(self, command, *values):
        if not isinstance(command, Command):
            raise ValueError("Invalid command type.")
        self.command = command
        self.values = values

    def __str__(self):
        return f"{self.command.value}: {self.values}"
    
    # Creazione del dizionario con command e values
    def to_dict(self):
        return {
            "command": self.command.value,
            "values": self.values
        }

    # Creazione del JSON relativo al dizionario per poterlo mandare con le socket
    def to_json(self):
        return json.dumps(self.to_dict())

    # Metodi di classe per creare i messaggi
    @classmethod
    def fly_up(cls, value):
        return cls(Command.FLY_UP, value)
    
    @classmethod
    def translate(cls, x, y, z, r):
        return cls(Command.TRANSLATE, x, y, z, r)
    
    @classmethod
    def land_at(cls, x, y, z, r):
        return cls(Command.LAND_AT, x, y, z, r)
    
    @classmethod
    def land(cls):
        return cls(Command.LAND)
    
    @classmethod
    def quit(cls):
        return cls(Command.QUIT)