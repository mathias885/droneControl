from enum import Enum
import json


# per mathias, questo sarebbe l'enum, in sostanza hai questi 5 campi e
# ognuno ha una stringa assegnata che identifica che tipo di int ha
# meters ha solo un int, coordinates ha una tupla di int
# nel server in stostanza lo faccio diventare un oggetto e poi uso .value per accedere ai valori

class Command(Enum):
    FLY_UP = "meters"
    TRANSLATE = "meters"
    LAND_AT = "coordinates"
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
    
    # qui creo il dizionario con command e values
    def to_dict(self):
        return {
            "command": self.command.value,
            "values": self.values
        }

    # qui creo il json relativo al dizionario per poterlo mandare con le socket
    def to_json(self):
        return json.dumps(self.to_dict())

    # questi permettono di creare gli enum in modo carino e semplice
    @classmethod
    def fly_up(cls, value):
        return cls(Command.FLY_UP, value)
    
    @classmethod
    def translate(cls, x, y):
        return cls(Command.TRANSLATE, x, y)
    
    @classmethod
    def land_at(cls, lat, lon):
        return cls(Command.LAND_AT, lat, lon)
    
    @classmethod
    def land(cls):
        return cls(Command.LAND)
    
    @classmethod
    def quit(cls):
        return cls(Command.QUIT)