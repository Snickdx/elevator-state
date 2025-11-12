from App.database import db

from abc import ABC, abstractmethod


class FloorState(ABC):
    @abstractmethod
    def groundFloor(self, elevator):
        pass

    @abstractmethod
    def firstFloor(self, elevator):
        pass

class FirstFloor(FloorState):
    
    def __init__(self):
        self.value = "first"
    
    def groundFloor(self, elevator):
        elevator.set_door_state(ClosedDoor())
        elevator.set_floor_state(GroundFloor())
        elevator.set_door_state(OpenDoor())
        print("Moving to the ground floor.")

    def firstFloor(self, elevator):
        print("Already on the first floor.")


class GroundFloor(FloorState):
    
    def __init__(self):
        self.value = "ground"

    def groundFloor(self, elevator):
        print("Already on the ground floor.")

    def firstFloor(self, elevator):
        elevator.set_door_state(ClosedDoor())
        elevator.set_floor_state(FirstFloor())
        elevator.set_door_state(OpenDoor())
        print("Moving to the first floor.")
    

class DoorState(ABC):
    @abstractmethod
    def openDoor(self, elevator):
        pass

    @abstractmethod
    def closeDoor(self, elevator):
        pass


class OpenDoor(DoorState):
    
    def __init__(self):
        self.value = "open"
    
    def openDoor(self, elevator):
        print("Door is already open.")

    def closeDoor(self, elevator):
        # Use the Elevator's setter so the change is persisted to DB
        elevator.set_door_state(ClosedDoor())
        print("Closing the door.")

class ClosedDoor(DoorState):

    def __init__(self):
        self.value = "closed"

    def openDoor(self, elevator):
        # Use the Elevator's setter so the change is persisted to DB
        elevator.set_door_state(OpenDoor())
        print("Opening the door.")

    def closeDoor(self, elevator):
        print("Door is already closed.")