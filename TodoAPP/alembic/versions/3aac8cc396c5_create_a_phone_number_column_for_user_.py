"""Create a phone_number column for user table 

Revision ID: 3aac8cc396c5
Revises: 
Create Date: 2026-05-11 17:06:00.007751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3aac8cc396c5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable= True))
    


def downgrade() -> None:
    op.drop_column('users','phone_number')
