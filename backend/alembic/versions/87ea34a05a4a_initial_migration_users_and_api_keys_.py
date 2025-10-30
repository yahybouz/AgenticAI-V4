"""Initial migration: users and api_keys tables

Revision ID: 87ea34a05a4a
Revises: 
Create Date: 2025-10-30 20:33:43.195330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87ea34a05a4a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, default='user'),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('max_agents', sa.Integer(), nullable=False, default=50),
        sa.Column('max_documents', sa.Integer(), nullable=False, default=1000),
        sa.Column('max_storage_mb', sa.Integer(), nullable=False, default=5000),
        sa.Column('default_model', sa.String(100), nullable=False, default='qwen2.5:14b'),
        sa.Column('language', sa.String(10), nullable=False, default='fr'),
        sa.Column('timezone', sa.String(50), nullable=False, default='UTC'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )

    # Create composite indexes for users
    op.create_index('idx_user_status_role', 'users', ['status', 'role'])
    op.create_index('idx_user_created_at', 'users', ['created_at'])

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('key_hash', sa.String(64), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )

    # Create composite index for api_keys
    op.create_index('idx_apikey_user_active', 'api_keys', ['user_id', 'is_active'])

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_api_keys_user_id', 'api_keys', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key first
    op.drop_constraint('fk_api_keys_user_id', 'api_keys', type_='foreignkey')

    # Drop indexes
    op.drop_index('idx_apikey_user_active', table_name='api_keys')
    op.drop_index('idx_user_created_at', table_name='users')
    op.drop_index('idx_user_status_role', table_name='users')

    # Drop tables
    op.drop_table('api_keys')
    op.drop_table('users')
