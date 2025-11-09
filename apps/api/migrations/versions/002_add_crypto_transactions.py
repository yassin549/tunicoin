"""Add crypto_transactions table

Revision ID: 002
Revises: 001
Create Date: 2024-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create crypto_transactions table."""
    
    op.create_table(
        'crypto_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('accounts.id'), nullable=True, index=True),
        sa.Column('transaction_type', sa.String(20), nullable=False, index=True),
        sa.Column('crypto_currency', sa.String(10), nullable=False),
        sa.Column('crypto_amount', sa.Numeric(18, 8), nullable=False),
        sa.Column('usd_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('exchange_rate', sa.Numeric(18, 8), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        sa.Column('payment_id', sa.String(255), nullable=True, index=True),
        sa.Column('invoice_id', sa.String(255), nullable=True),
        sa.Column('payment_url', sa.String(512), nullable=True),
        sa.Column('txn_hash', sa.String(255), nullable=True),
        sa.Column('blockchain_network', sa.String(50), nullable=True),
        sa.Column('confirmations', sa.Integer, nullable=False, default=0),
        sa.Column('recipient_address', sa.String(255), nullable=True),
        sa.Column('withdrawal_fee', sa.Numeric(12, 2), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.Column('confirmed_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create indexes for better query performance
    op.create_index('idx_crypto_tx_user_type', 'crypto_transactions', ['user_id', 'transaction_type'])
    op.create_index('idx_crypto_tx_user_status', 'crypto_transactions', ['user_id', 'status'])
    op.create_index('idx_crypto_tx_created', 'crypto_transactions', ['created_at'])


def downgrade() -> None:
    """Drop crypto_transactions table."""
    
    op.drop_index('idx_crypto_tx_created', 'crypto_transactions')
    op.drop_index('idx_crypto_tx_user_status', 'crypto_transactions')
    op.drop_index('idx_crypto_tx_user_type', 'crypto_transactions')
    op.drop_table('crypto_transactions')
