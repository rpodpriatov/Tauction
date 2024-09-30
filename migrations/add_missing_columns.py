from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add missing columns to users table
    op.add_column('users', sa.Column('email', sa.String(120), nullable=True))
    
    # Add missing columns to auctions table
    op.add_column('auctions', sa.Column('starting_price', sa.Float(), nullable=True))
    op.add_column('auctions', sa.Column('auction_type', sa.String(20), nullable=True))
    op.add_column('auctions', sa.Column('current_dutch_price', sa.Float(), nullable=True))
    op.add_column('auctions', sa.Column('dutch_price_decrement', sa.Float(), nullable=True))
    op.add_column('auctions', sa.Column('dutch_interval', sa.Integer(), nullable=True))

def downgrade():
    # Remove added columns from users table
    op.drop_column('users', 'email')
    
    # Remove added columns from auctions table
    op.drop_column('auctions', 'starting_price')
    op.drop_column('auctions', 'auction_type')
    op.drop_column('auctions', 'current_dutch_price')
    op.drop_column('auctions', 'dutch_price_decrement')
    op.drop_column('auctions', 'dutch_interval')
