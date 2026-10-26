"""drop badge_type from monopolies

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-10-26 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f6a7b8c9d0e1'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('monopolies') as batch:
        batch.drop_column('badge_type')


def downgrade():
    with op.batch_alter_table('monopolies') as batch:
        batch.add_column(sa.Column('badge_type', sa.String(length=20), nullable=True))