"""Add plugin, policy, and job tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: str = '001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create plugin_states table
    op.create_table(
        'plugin_states',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plugin_name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('degraded', sa.Boolean(), nullable=False),
        sa.Column('last_error', sa.String(length=1000), nullable=True),
        sa.Column('loaded_at', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute(sa.text("COMMENT ON TABLE plugin_states IS 'Tracks plugin state per guild and globally'"))
    op.create_index(op.f('ix_plugin_states_plugin_name'), 'plugin_states', ['plugin_name'], unique=False)
    op.create_index(op.f('ix_plugin_states_guild_id'), 'plugin_states', ['guild_id'], unique=False)

    # Create policy_rules table
    op.create_table(
        'policy_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scope_type', sa.String(length=20), nullable=False),
        sa.Column('scope_id', sa.BigInteger(), nullable=True),
        sa.Column('capability', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute(sa.text("COMMENT ON TABLE policy_rules IS 'Policy rules for capability-based access control'"))
    op.create_index(op.f('ix_policy_rules_scope_type'), 'policy_rules', ['scope_type'], unique=False)
    op.create_index(op.f('ix_policy_rules_scope_id'), 'policy_rules', ['scope_id'], unique=False)
    op.create_index(op.f('ix_policy_rules_capability'), 'policy_rules', ['capability'], unique=False)

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('locked_by', sa.String(length=100), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute(sa.text("COMMENT ON TABLE jobs IS 'Background jobs for durable task execution'"))
    op.create_index(op.f('ix_jobs_job_type'), 'jobs', ['job_type'], unique=False)
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
    op.create_index(op.f('ix_jobs_next_run_at'), 'jobs', ['next_run_at'], unique=False)
    op.create_index(op.f('ix_jobs_idempotency_key'), 'jobs', ['idempotency_key'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_jobs_idempotency_key'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_next_run_at'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_job_type'), table_name='jobs')
    op.drop_table('jobs')

    op.drop_index(op.f('ix_policy_rules_capability'), table_name='policy_rules')
    op.drop_index(op.f('ix_policy_rules_scope_id'), table_name='policy_rules')
    op.drop_index(op.f('ix_policy_rules_scope_type'), table_name='policy_rules')
    op.drop_table('policy_rules')

    op.drop_index(op.f('ix_plugin_states_guild_id'), table_name='plugin_states')
    op.drop_index(op.f('ix_plugin_states_plugin_name'), table_name='plugin_states')
    op.drop_table('plugin_states')
