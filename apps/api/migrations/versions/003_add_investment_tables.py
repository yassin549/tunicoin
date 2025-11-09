"""Add investment management tables

Revision ID: 003
Revises: 002
Create Date: 2025-11-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create investment management tables."""
    
    # 1. Investment Tiers Table
    op.create_table(
        'investment_tiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('minimum_deposit', sa.Float, nullable=False),
        sa.Column('monthly_return_percentage', sa.Float, nullable=False),
        sa.Column('annual_roi_percentage', sa.Float, nullable=False),
        sa.Column('features', postgresql.JSON, nullable=False, default={}),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # 2. Investment Accounts Table
    op.create_table(
        'investment_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('tier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('investment_tiers.id'), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending_kyc'),
        sa.Column('initial_deposit', sa.Float, nullable=False, default=0.0),
        sa.Column('current_balance', sa.Float, nullable=False, default=0.0),
        sa.Column('total_returns', sa.Float, nullable=False, default=0.0),
        sa.Column('total_withdrawn', sa.Float, nullable=False, default=0.0),
        sa.Column('total_deposited', sa.Float, nullable=False, default=0.0),
        sa.Column('last_payout_at', sa.DateTime, nullable=True),
        sa.Column('next_payout_at', sa.DateTime, nullable=True),
        sa.Column('opened_at', sa.DateTime, nullable=False),
        sa.Column('activated_at', sa.DateTime, nullable=True),
        sa.Column('closed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # 3. Deposits Table
    op.create_table(
        'deposits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('investment_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('investment_accounts.id'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, default='USD'),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('transaction_hash', sa.String(255), nullable=True),
        sa.Column('payment_provider', sa.String(50), nullable=True),
        sa.Column('provider_transaction_id', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending', index=True),
        sa.Column('confirmed_at', sa.DateTime, nullable=True),
        sa.Column('failed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('admin_notes', sa.String, nullable=True),
    )
    
    # 4. Investment Returns Table
    op.create_table(
        'investment_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('investment_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('investment_accounts.id'), nullable=False, index=True),
        sa.Column('period_start', sa.Date, nullable=False, index=True),
        sa.Column('period_end', sa.Date, nullable=False, index=True),
        sa.Column('period_type', sa.String(20), nullable=False, default='daily'),
        sa.Column('expected_return', sa.Float, nullable=False, default=0.0),
        sa.Column('actual_return', sa.Float, nullable=False, default=0.0),
        sa.Column('return_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('balance_before', sa.Float, nullable=False, default=0.0),
        sa.Column('balance_after', sa.Float, nullable=False, default=0.0),
        sa.Column('status', sa.String(20), nullable=False, default='projected'),
        sa.Column('credited_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('notes', sa.String, nullable=True),
    )
    
    # 5. Payouts Table
    op.create_table(
        'payouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('investment_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('investment_accounts.id'), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('payout_method', sa.String(50), nullable=False),
        sa.Column('destination', sa.String(500), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, default='USD'),
        sa.Column('status', sa.String(20), nullable=False, default='pending', index=True),
        sa.Column('transaction_hash', sa.String(255), nullable=True),
        sa.Column('provider_transaction_id', sa.String(255), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('admin_notes', sa.String, nullable=True),
        sa.Column('rejection_reason', sa.String, nullable=True),
        sa.Column('requested_at', sa.DateTime, nullable=False),
        sa.Column('approved_at', sa.DateTime, nullable=True),
        sa.Column('processed_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('rejected_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # 6. KYC Submissions Table
    op.create_table(
        'kyc_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, unique=True, index=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending', index=True),
        sa.Column('kyc_provider', sa.String(50), nullable=True),
        sa.Column('provider_reference_id', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('date_of_birth', sa.Date, nullable=False),
        sa.Column('nationality', sa.String(50), nullable=True),
        sa.Column('id_type', sa.String(50), nullable=False),
        sa.Column('id_number_encrypted', sa.String, nullable=True),
        sa.Column('id_expiry_date', sa.Date, nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=False),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=False),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('is_accredited_investor', sa.Boolean, nullable=False, default=False),
        sa.Column('accreditation_proof', sa.String, nullable=True),
        sa.Column('documents', postgresql.JSON, nullable=False, default={}),
        sa.Column('submitted_at', sa.DateTime, nullable=False),
        sa.Column('reviewed_at', sa.DateTime, nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('rejection_reason', sa.String, nullable=True),
        sa.Column('sanctions_check_passed', sa.Boolean, nullable=False, default=False),
        sa.Column('sanctions_check_date', sa.DateTime, nullable=True),
        sa.Column('aml_risk_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create additional indexes for better query performance
    op.create_index('idx_inv_acct_user_status', 'investment_accounts', ['user_id', 'status'])
    op.create_index('idx_inv_acct_tier', 'investment_accounts', ['tier_id'])
    op.create_index('idx_deposits_user_status', 'deposits', ['user_id', 'status'])
    op.create_index('idx_payouts_user_status', 'payouts', ['user_id', 'status'])
    op.create_index('idx_returns_account_period', 'investment_returns', ['investment_account_id', 'period_start', 'period_end'])
    op.create_index('idx_kyc_status', 'kyc_submissions', ['status'])


def downgrade() -> None:
    """Drop investment management tables."""
    
    # Drop indexes first
    op.drop_index('idx_kyc_status', 'kyc_submissions')
    op.drop_index('idx_returns_account_period', 'investment_returns')
    op.drop_index('idx_payouts_user_status', 'payouts')
    op.drop_index('idx_deposits_user_status', 'deposits')
    op.drop_index('idx_inv_acct_tier', 'investment_accounts')
    op.drop_index('idx_inv_acct_user_status', 'investment_accounts')
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('kyc_submissions')
    op.drop_table('payouts')
    op.drop_table('investment_returns')
    op.drop_table('deposits')
    op.drop_table('investment_accounts')
    op.drop_table('investment_tiers')
