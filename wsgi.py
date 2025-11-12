import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User, Elevator
from App.main import create_app
from App.controllers import ( create_elevator, create_user, get_all_users_json, get_all_users, initialize )
from App.models.state import GroundFloor, FirstFloor, OpenDoor, ClosedDoor


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)


@app.cli.command("elevator", help="Interactive elevator CLI to operate the Elevator model")
def elevator_cli():
    """Starts a simple REPL to operate the Elevator model using the state implementations.

    Commands:
      open    - open the door
      close   - close the door
      up      - move to the first floor
      down    - move to the ground floor
      status  - show current floor and door state
      help    - show this help
      quit    - exit the CLI
    """
    # List existing elevators and prompt the user to select which persisted
    # elevator to operate. Elevator rows should be created by `flask init`.
    try:
        elevators = Elevator.query.all()
    except Exception as e:
        click.echo(f"Database not available or import error: {e}")
        return

    if not elevators:
        click.echo("No elevators found. Run 'flask init' to create elevators before using this command.")
        return

    click.echo("Available elevators:")
    for e in elevators:
        click.echo(f"  id: {e.id}  Floor: {e.floor}  Door: {e.door}")

    selected = None
    while selected is None:
        choice = input("Select elevator id to operate (or 'q' to quit): ").strip().lower()
        if choice in ("q", "quit"):
            click.echo('Goodbye.')
            return
        try:
            eid = int(choice)
            selected = Elevator.query.get(eid)
            if not selected:
                click.echo("Invalid elevator id; try again.")
                selected = None
        except ValueError:
            click.echo("Please enter a numeric elevator id.")

    elevator = selected
    # Rehydrate runtime state objects from persisted values
    if getattr(elevator, 'floor', None) == 'ground':
        elevator.set_floor_state(GroundFloor())
    else:
        elevator.set_floor_state(FirstFloor())

    if getattr(elevator, 'door', None) == 'open':
        elevator.set_door_state(OpenDoor())
    else:
        elevator.set_door_state(ClosedDoor())
    click.echo("  close        - close the door")
    click.echo("  first_floor  - move to the first floor")
    click.echo("  ground_floor - move to the ground floor")
    click.echo("  switch       - switch to a different elevator")
    click.echo("  help         - show this help")
    click.echo("  quit         - exit the CLI")

    def print_state():
        # print the selected elevator's persistent values if present,
        # otherwise fall back to runtime state names
        floor = getattr(elevator, 'floor', None)
        door = getattr(elevator, 'door', None)
        if not floor and hasattr(elevator, 'floor_state'):
            floor = type(elevator.floor_state).__name__
        if not door and hasattr(elevator, 'door_state'):
            door = type(elevator.door_state).__name__
        click.echo(f"Current state -> Floor: {floor}, Door: {door}")
    while True:
        try:
            cmd = input("elevator> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            click.echo('\nExiting elevator CLI.')
            break

        if not cmd:
            continue

        if cmd in ("quit", "exit"):
            click.echo('Goodbye.')
            break
        elif cmd == "help":
            click.echo("Commands: open, close, first_floor, ground_floor, switch, help, quit")
        elif cmd == "open":
            elevator.open_door()
            print_state()
        elif cmd == "close":
            elevator.close_door()
            print_state()
        elif cmd in ("first_floor", "first-floor", "first", "up"):
            elevator.first_floor()
            print_state()
        elif cmd in ("ground_floor", "ground-floor", "ground", "down"):
            elevator.ground_floor()
            print_state()
        elif cmd == "switch":
            # list and let user choose another elevator
            elevators = Elevator.query.all()
            click.echo("Available elevators:")
            for e in elevators:
                click.echo(f"  id: {e.id}  Floor: {e.floor}  Door: {e.door}")
            choice = input("Select elevator id to switch to: ").strip()
            try:
                eid = int(choice)
                selected = Elevator.query.get(eid)
                if selected:
                    elevator = selected
                    # rehydrate states using setters so persistence is consistent
                    if getattr(elevator, 'floor', None) == 'ground':
                        elevator.set_floor_state(GroundFloor())
                    else:
                        elevator.set_floor_state(FirstFloor())
                    if getattr(elevator, 'door', None) == 'open':
                        elevator.set_door_state(OpenDoor())
                    else:
                        elevator.set_door_state(ClosedDoor())
                    click.echo(f"Switched to elevator {eid}")
                    print_state()
                else:
                    click.echo("Invalid elevator id.")
            except ValueError:
                click.echo("Enter a numeric id.")
        elif cmd == "status":
            floor = type(elevator.floor_state).__name__ if hasattr(elevator, 'floor_state') else 'Unknown'
            door = type(elevator.door_state).__name__ if hasattr(elevator, 'door_state') else 'Unknown'
            click.echo(f"Floor: {floor}, Door: {door}")
        else:
            click.echo("Unknown command; type 'help'.")
