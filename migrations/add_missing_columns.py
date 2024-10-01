from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add missing columns to users table
    op.add_column('users', sa.Column('email', sa.String(120), nullable=True))
    
    # Add missing columns to auctions table
    op.add_column('auctions', sa.Column('starting_price', sa.Float(), nullable=True))

def downgrade():
    # Remove added columns from users table
    op.drop_column('users', 'email')
    
    # Remove added columns from auctions table
    op.drop_column('auctions', 'starting_price')
