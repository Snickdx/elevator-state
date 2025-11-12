from App.models.elevator import Elevator
from App.database import db


def create_elevator():
    elevator = Elevator()
    db.session.add(elevator)
    db.session.commit()
    return elevator