"""add authentication fields to users

Revision ID: 7f3a9c21d5e4
Revises: 45c1d8937ec0
Create Date: 2026-09-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f3a9c21d5e4'
down_revision: Union[str, Sequence[str], None] = '45c1d8937ec0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite no permite agregar una columna NOT NULL sin un valor por
    # defecto, incluso en una tabla vacia. Por eso se agrega con un
    # server_default temporal y luego se retira, dejando la columna
    # NOT NULL y sin default en el modelo (igual que en user_model.py).
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('hashed_password', sa.String(), nullable=False, server_default='')
        )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('hashed_password')
