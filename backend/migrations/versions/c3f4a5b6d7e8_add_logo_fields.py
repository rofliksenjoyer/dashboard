"""add logo fields to monopoly

Revision ID: c3f4a5b6d7e8
Revises: b2e3f4a5c6d7
Create Date: 2026-10-25 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c3f4a5b6d7e8'
down_revision = 'b2e3f4a5c6d7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('monopolies') as batch:
        batch.add_column(sa.Column('logo_url', sa.String(length=500), nullable=True))
        batch.add_column(sa.Column('logo_filename', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('monopolies') as batch:
        batch.drop_column('logo_filename')
        batch.drop_column('logo_url')