from enum import Enum
import json

class message(Enum):
    fly_up = "meters"
    translate = "meters"
    land_at = "coordinates"
    land = "none"
    quit = "none"

    def __call__(self, *args):
        if self == message.fly_up or self == message.translate:
            if len(args) == 1 and isinstance(args[0], int):
                self.data = {"meters": args[0]}
            else:
                raise ValueError("Expected one integer for meters.")
        
        elif self == message.land_at:
            if len(args) == 2 and all(isinstance(arg, int) for arg in args):
                self.data = {"coordinates": (args[0], args[1])}
            else:
                raise ValueError("Expected two integers for coordinates.")
        
        elif self == message.land or self == message.quit:
            if args:
                raise ValueError("No arguments expected for this message type.")
            self.data = None
        
        return self
    
    def getValue(self):
        return list(self.data.values())[0] if self.data else None
    
    def getJson(self):
        return json.dumps({"type": self.name, "value": self.getValue()})

    @staticmethod
    def loadJson(data_json):
        data = json.loads(data_json)
        match data['type']:
            case "fly_up":
                return message.fly_up(data['value'])
            case "translate":
                return message.translate(data['value'])
            case "land_at":
                return message.land_at(*data['value'])  # Assuming land_at takes a tuple of coordinates
            case "land":
                return message.land()
            case "quit":
                return message.quit()
            case _:
                raise ValueError(f"Unknown message type: {data['type']}")
