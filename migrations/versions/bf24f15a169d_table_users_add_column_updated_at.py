"""table users add column updated_at

Revision ID: bf24f15a169d
Revises: a26efcd7cd87
Create Date: 2024-12-17 17:27:08.035796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf24f15a169d'
down_revision: Union[str, None] = 'a26efcd7cd87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'updated_at')
