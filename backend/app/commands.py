import click
from flask.cli import with_appcontext

from app.auth.models import User, UserRole
from app.extensions import db


@click.command("make-admin")
@click.argument("email")
@with_appcontext
def make_admin_command(email):
    """Promote an existing user to admin."""
    user = User.query.filter_by(email=email).first()
    if not user:
        click.echo(f"Error: no user found with email '{email}'", err=True)
        raise SystemExit(1)
    user.role = UserRole.ADMIN
    db.session.commit()
    click.echo(f"Done: {email} is now an admin.")
