from .user import create_user
from .elevator import create_elevator
from App.database import db


def initialize():
    # recreate schema
    db.drop_all()
    db.create_all()
    # seed a default user
    create_user('bob', 'bobpass')
    # create two elevators so CLI can operate persisted elevators
    create_elevator()
    create_elevator()
