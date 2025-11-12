from App.database import db
from App.models.state import GroundFloor, OpenDoor, ClosedDoor



class Elevator(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.String(10))
    door = db.Column(db.String(10))
    floor_state = None
    door_state = None

    def __init__(self):
        # initialize elevator to the ground floor with doors closed
        self.set_door_state(ClosedDoor())
        self.set_floor_state(GroundFloor())


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
        self.floor = state.value
        db.session.add(self)
        db.session.commit()

    def set_door_state(self, state):
        self.door_state = state
        self.door = state.value
        db.session.add(self)
        db.session.commit()