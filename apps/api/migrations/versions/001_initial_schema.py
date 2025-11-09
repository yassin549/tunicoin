"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-11-07

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('twofa_secret', sa.String(length=255), nullable=True),
        sa.Column('twofa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('plan_id', sa.String(length=50), nullable=True, server_default='free'),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('next_billing_date', sa.DateTime(), nullable=True),
        sa.Column('kyc_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('kyc_verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])

    # Create instruments table
    op.create_table(
        'instruments',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('instrument_type', sa.String(length=50), nullable=False),
        sa.Column('tick_size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('contract_size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('base_currency', sa.String(length=10), nullable=False),
        sa.Column('quote_currency', sa.String(length=10), nullable=False),
        sa.Column('base_spread', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('funding_rate', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('slippage_factor', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('min_size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('max_size', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_tradeable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol'),
    )
    op.create_index(op.f('ix_instruments_symbol'), 'instruments', ['symbol'])

    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('base_currency', sa.String(length=10), nullable=False),
        sa.Column('balance', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('equity', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('margin_used', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('margin_available', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_leverage', sa.Integer(), nullable=False),
        sa.Column('max_daily_loss', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'])

    # Create candles table
    op.create_table(
        'candles',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('instrument_id', UUID(), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('high', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('low', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('close', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('volume', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_candles_instrument_id'), 'candles', ['instrument_id'])
    op.create_index(op.f('ix_candles_timeframe'), 'candles', ['timeframe'])
    op.create_index(op.f('ix_candles_timestamp'), 'candles', ['timestamp'])
    # Composite index for efficient queries
    op.create_index('ix_candles_instrument_timeframe_timestamp', 'candles', ['instrument_id', 'timeframe', 'timestamp'])

    # Create bots table
    op.create_table(
        'bots',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('account_id', UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('strategy_id', sa.String(length=100), nullable=False),
        sa.Column('params', JSON, nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('max_position_size', sa.Float(), nullable=False),
        sa.Column('max_daily_loss', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('total_trades', sa.Integer(), nullable=False),
        sa.Column('winning_trades', sa.Integer(), nullable=False),
        sa.Column('losing_trades', sa.Integer(), nullable=False),
        sa.Column('total_pnl', sa.Float(), nullable=False),
        sa.Column('is_circuit_broken', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('circuit_breaker_reason', sa.String(length=500), nullable=True),
        sa.Column('last_execution_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_bots_user_id'), 'bots', ['user_id'])
    op.create_index(op.f('ix_bots_account_id'), 'bots', ['account_id'])

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('account_id', UUID(), nullable=False),
        sa.Column('instrument_id', UUID(), nullable=False),
        sa.Column('order_type', sa.String(length=50), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('stop_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('filled_size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('fill_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('slippage', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('leverage', sa.Integer(), nullable=False),
        sa.Column('margin_required', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('bot_id', UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('filled_at', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ),
        sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_orders_account_id'), 'orders', ['account_id'])
    op.create_index(op.f('ix_orders_instrument_id'), 'orders', ['instrument_id'])
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'])

    # Create positions table
    op.create_table(
        'positions',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('account_id', UUID(), nullable=False),
        sa.Column('instrument_id', UUID(), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('size', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('entry_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('realized_pnl', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('leverage', sa.Integer(), nullable=False),
        sa.Column('margin_used', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('stop_loss', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('take_profit', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('funding_paid', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('last_funding_at', sa.DateTime(), nullable=True),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('bot_id', UUID(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ),
        sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_positions_account_id'), 'positions', ['account_id'])
    op.create_index(op.f('ix_positions_instrument_id'), 'positions', ['instrument_id'])
    op.create_index(op.f('ix_positions_is_open'), 'positions', ['is_open'])

    # Create ledger_entries table
    op.create_table(
        'ledger_entries',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('account_id', UUID(), nullable=False),
        sa.Column('entry_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('balance_after', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('order_id', UUID(), nullable=True),
        sa.Column('position_id', UUID(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('meta', JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ledger_entries_account_id'), 'ledger_entries', ['account_id'])
    op.create_index(op.f('ix_ledger_entries_entry_type'), 'ledger_entries', ['entry_type'])
    op.create_index(op.f('ix_ledger_entries_created_at'), 'ledger_entries', ['created_at'])

    # Create backtests table
    op.create_table(
        'backtests',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('strategy_id', sa.String(length=100), nullable=False),
        sa.Column('instrument_id', UUID(), nullable=False),
        sa.Column('params', JSON, nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('initial_capital', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('metrics', JSON, nullable=True),
        sa.Column('trade_log_url', sa.String(length=500), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_backtests_user_id'), 'backtests', ['user_id'])
    op.create_index(op.f('ix_backtests_created_at'), 'backtests', ['created_at'])

    # Create bot_decisions table
    op.create_table(
        'bot_decisions',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('bot_id', UUID(), nullable=False),
        sa.Column('account_id', UUID(), nullable=False),
        sa.Column('candle_timestamp', sa.DateTime(), nullable=False),
        sa.Column('instrument_id', UUID(), nullable=False),
        sa.Column('indicators', JSON, nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.String(length=1000), nullable=False),
        sa.Column('proposed_order', JSON, nullable=True),
        sa.Column('order_id', UUID(), nullable=True),
        sa.Column('final_order', JSON, nullable=True),
        sa.Column('risk_adjusted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('risk_adjustment_reason', sa.String(length=500), nullable=True),
        sa.Column('executed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('execution_result', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_bot_decisions_bot_id'), 'bot_decisions', ['bot_id'])
    op.create_index(op.f('ix_bot_decisions_account_id'), 'bot_decisions', ['account_id'])
    op.create_index(op.f('ix_bot_decisions_candle_timestamp'), 'bot_decisions', ['candle_timestamp'])
    op.create_index(op.f('ix_bot_decisions_created_at'), 'bot_decisions', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order due to foreign keys
    op.drop_table('bot_decisions')
    op.drop_table('backtests')
    op.drop_table('ledger_entries')
    op.drop_table('positions')
    op.drop_table('orders')
    op.drop_table('bots')
    op.drop_table('candles')
    op.drop_table('accounts')
    op.drop_table('instruments')
    op.drop_table('users')
