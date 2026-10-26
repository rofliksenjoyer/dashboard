"""add notes, industry descriptions and country flag

Revision ID: b2e3f4a5c6d7
Revises: a1f2c3d4e5f6
Create Date: 2026-10-21 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b2e3f4a5c6d7'
down_revision = 'a1f2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('countries') as batch:
        batch.add_column(sa.Column('flag_emoji', sa.String(8), nullable=True))

    op.create_table(
        'country_industry_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('industry_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('body', sa.Text(), nullable=False, server_default=''),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['industry_id'], ['industries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country_id', 'industry_id'),
    )
    op.create_index('ix_note_country_industry', 'country_industry_notes',
                    ['country_id', 'industry_id'])


def downgrade():
    op.drop_index('ix_note_country_industry', table_name='country_industry_notes')
    op.drop_table('country_industry_notes')
    with op.batch_alter_table('countries') as batch:
        batch.drop_column('flag_emoji')