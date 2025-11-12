import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User, Elevator
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )


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
    elevator = Elevator()
    # Initialize elevator on the ground floor with doors closed.
    # Use direct state assignment for initialization so the CLI uses the
    # public movement methods (ground_floor/first_floor) to change floors
    # rather than calling the (considered) private setter methods.


    click.echo("Elevator CLI started. Type 'help' for commands. Ctrl-C or 'quit' to exit.")
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
            click.echo("Commands: open, close, up, down, status, help, quit")
        elif cmd == "open":
            elevator.open_door()
        elif cmd == "close":
            elevator.close_door()
        elif cmd in ("up", "first"):
            elevator.first_floor()
        elif cmd in ("down", "ground"):
            elevator.ground_floor()
        elif cmd == "status":
            floor = type(elevator.floor_state).__name__ if hasattr(elevator, 'floor_state') else 'Unknown'
            door = type(elevator.door_state).__name__ if hasattr(elevator, 'door_state') else 'Unknown'
            click.echo(f"Floor: {floor}, Door: {door}")
        else:
            click.echo("Unknown command; type 'help'.")
