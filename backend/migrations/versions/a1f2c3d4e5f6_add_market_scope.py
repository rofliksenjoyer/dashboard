"""add market scope and monopoly profile fields

Revision ID: a1f2c3d4e5f6
Revises: dc0294717836
Create Date: 2026-10-20 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1f2c3d4e5f6'
down_revision = 'dc0294717836'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('countries') as batch:
        batch.add_column(sa.Column('market_scope', sa.String(10), nullable=False, server_default='ru'))
    op.create_index('ix_country_market_scope', 'countries', ['market_scope'])

    with op.batch_alter_table('monopolies') as batch:
        batch.add_column(sa.Column('short_name', sa.String(100), nullable=True))
        batch.add_column(sa.Column('color', sa.String(20), nullable=True))
        batch.add_column(sa.Column('badge_type', sa.String(20), nullable=True))
        batch.add_column(sa.Column('activity', sa.Text(), nullable=True))
        batch.add_column(sa.Column('employees', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('founded_year', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('hq', sa.String(200), nullable=True))
    op.create_index('ix_monopoly_country_industry', 'monopolies', ['country_id', 'industry_id'])

    with op.batch_alter_table('periods') as batch:
        batch.create_index('ix_period_year', ['year'])


def downgrade():
    with op.batch_alter_table('periods') as batch:
        batch.drop_index('ix_period_year')

    op.drop_index('ix_monopoly_country_industry', table_name='monopolies')
    with op.batch_alter_table('monopolies') as batch:
        for col in ['short_name', 'color', 'badge_type', 'activity',
                    'employees', 'founded_year', 'hq']:
            batch.drop_column(col)

    op.drop_index('ix_country_market_scope', table_name='countries')
    with op.batch_alter_table('countries') as batch:
        batch.drop_column('market_scope')