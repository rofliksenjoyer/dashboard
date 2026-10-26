"""add hhi and top_share overrides to notes

Revision ID: d4e5f6a7b8c9
Revises: c3f4a5b6d7e8
Create Date: 2026-10-26 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e5f6a7b8c9'
down_revision = 'c3f4a5b6d7e8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('country_industry_notes') as batch:
        batch.add_column(sa.Column('hhi_override', sa.Float(), nullable=True))
        batch.add_column(sa.Column('top_share_override', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('country_industry_notes') as batch:
        batch.drop_column('top_share_override')
        batch.drop_column('hhi_override')