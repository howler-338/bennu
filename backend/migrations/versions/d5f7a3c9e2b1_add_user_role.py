"""add user role

Revision ID: d5f7a3c9e2b1
Revises: c4e9a7b2f1d8
Create Date: 2026-05-29 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5f7a3c9e2b1'
down_revision = 'c4e9a7b2f1d8'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE TYPE userrole AS ENUM ('USER', 'ADMIN')")
    op.add_column('users', sa.Column(
        'role',
        sa.Enum('USER', 'ADMIN', name='userrole'),
        nullable=False,
        server_default='USER',
    ))


def downgrade():
    op.drop_column('users', 'role')
    op.execute("DROP TYPE userrole")
