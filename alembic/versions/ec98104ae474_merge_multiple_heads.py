"""merge multiple heads

Revision ID: ec98104ae474
Revises: 7b31879a319c, add_winner_id_to_auctions
Create Date: 2024-09-29 14:08:34.217577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec98104ae474'
down_revision: Union[str, None] = ('7b31879a319c', 'add_winner_id_to_auctions')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
