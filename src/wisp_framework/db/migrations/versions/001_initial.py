"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create guild_configs table
    op.create_table(
        'guild_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('welcome_channel_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id')
    )
    op.create_index(op.f('ix_guild_configs_guild_id'), 'guild_configs', ['guild_id'], unique=False)

    # Create module_states table
    op.create_table(
        'module_states',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Comment('Tracks which modules are enabled/disabled per guild')
    )
    op.create_index(op.f('ix_module_states_guild_id'), 'module_states', ['guild_id'], unique=False)
    op.create_index(op.f('ix_module_states_module_name'), 'module_states', ['module_name'], unique=False)

    # Create guild_data table
    op.create_table(
        'guild_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Comment('Generic key-value storage for per-guild data')
    )
    op.create_index(op.f('ix_guild_data_guild_id'), 'guild_data', ['guild_id'], unique=False)
    op.create_index(op.f('ix_guild_data_key'), 'guild_data', ['key'], unique=False)
    op.create_index(op.f('ix_guild_data_module_name'), 'guild_data', ['module_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_guild_data_module_name'), table_name='guild_data')
    op.drop_index(op.f('ix_guild_data_key'), table_name='guild_data')
    op.drop_index(op.f('ix_guild_data_guild_id'), table_name='guild_data')
    op.drop_table('guild_data')
    
    op.drop_index(op.f('ix_module_states_module_name'), table_name='module_states')
    op.drop_index(op.f('ix_module_states_guild_id'), table_name='module_states')
    op.drop_table('module_states')
    
    op.drop_index(op.f('ix_guild_configs_guild_id'), table_name='guild_configs')
    op.drop_table('guild_configs')
