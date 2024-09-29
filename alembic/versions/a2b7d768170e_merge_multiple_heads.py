"""merge multiple heads

Revision ID: a2b7d768170e
Revises: ec98104ae474
Create Date: 2024-09-29 15:07:26.362154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2b7d768170e'
down_revision: Union[str, None] = 'ec98104ae474'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
