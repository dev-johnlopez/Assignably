from app import create_app, db, cli
from app.cli import add_roles
from app.auth.models import User

app = create_app()
cli.register(app)
app.cli.add_command(add_roles)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
