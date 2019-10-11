import os
import click
from app import app
from flask.cli import with_appcontext
from app.auth.models import Role


def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        pass

    @translate.command()
    def update():
        """Update all languages."""
        pass

    @translate.command()
    def compile():
        """Compile all languages."""
        pass


@click.command("add_roles")
@with_appcontext
def add_roles():
    from app import db, security
    from app.auth.models import Role
    db.init_app(app)
    role = Role(name="Company Admin", description="Administrator of a company. \
                                                  Users with this role can modify \
                                                  company data.")
    db.session.add(role)
    db.session.commit()

    role = Role(name="Underwriter", description="Users with the ability to \
                                                evaluate deals.")
    db.session.add(role)
    db.session.commit()
