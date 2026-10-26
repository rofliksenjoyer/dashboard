"""monopoly types table

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-10-26 15:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7b8c9d0e1f2'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'monopoly_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    with op.batch_alter_table('monopolies') as batch:
        batch.add_column(sa.Column('monopoly_type_id', sa.Integer(), nullable=True))

    # Переносим старое текстовое поле в справочник
    op.execute("""
        INSERT INTO monopoly_types (name)
        SELECT DISTINCT monopoly_type FROM monopolies
        WHERE monopoly_type IS NOT NULL
    """)
    op.execute("""
        UPDATE monopolies m
        SET monopoly_type_id = mt.id
        FROM monopoly_types mt
        WHERE m.monopoly_type = mt.name
    """)

    with op.batch_alter_table('monopolies') as batch:
        batch.alter_column('monopoly_type_id', nullable=False)
        batch.create_foreign_key(
            'fk_monopolies_monopoly_type_id',
            'monopoly_types', ['monopoly_type_id'], ['id']
        )
        batch.drop_column('monopoly_type')


def downgrade():
    with op.batch_alter_table('monopolies') as batch:
        batch.add_column(sa.Column('monopoly_type', sa.String(length=50), nullable=True))

    op.execute("""
        UPDATE monopolies m
        SET monopoly_type = mt.name
        FROM monopoly_types mt
        WHERE m.monopoly_type_id = mt.id
    """)

    with op.batch_alter_table('monopolies') as batch:
        batch.alter_column('monopoly_type', nullable=False)
        batch.drop_constraint('fk_monopolies_monopoly_type_id', type_='foreignkey')
        batch.drop_column('monopoly_type_id')

    op.drop_table('monopoly_types')