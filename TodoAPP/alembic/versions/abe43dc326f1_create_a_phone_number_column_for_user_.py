"""Create a phone_number column for user table 

Revision ID: abe43dc326f1
Revises: 3aac8cc396c5
Create Date: 2026-05-11 17:19:45.530670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abe43dc326f1'
down_revision: Union[str, Sequence[str], None] = '3aac8cc396c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
