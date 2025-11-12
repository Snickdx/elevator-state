from App.models.state import GroundFloor, ClosedDoor


class Elevator():
    def __init__(self):
        # initialize elevator to the ground floor with doors closed
        self.floor_state = GroundFloor()
        self.door_state = ClosedDoor()

    def open_door(self):
        return self.door_state.openDoor(self)
    
    def close_door(self):
        return self.door_state.closeDoor(self)
    
    def first_floor(self):
        return self.floor_state.firstFloor(self)
    
    def ground_floor(self):
        return self.floor_state.groundFloor(self)

    def set_floor_state(self, state):
        self.floor_state = state

    def set_door_state(self, state):
        self.door_state = state