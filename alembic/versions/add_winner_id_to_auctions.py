"""Add winner_id to auctions

Revision ID: add_winner_id_to_auctions
Revises: <previous_revision_id>
Create Date: 2024-09-28 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_winner_id_to_auctions'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('auctions', sa.Column('winner_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_auctions_winner_id_users', 'auctions', 'users', ['winner_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_auctions_winner_id_users', 'auctions', type_='foreignkey')
    op.drop_column('auctions', 'winner_id')
