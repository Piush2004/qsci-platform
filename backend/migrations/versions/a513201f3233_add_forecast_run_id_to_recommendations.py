"""add forecast_run_id to recommendations

Revision ID: a513201f3233
Revises: 7ee0940aea90
Create Date: 2026-08-20 09:37:35.131419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a513201f3233'
down_revision: Union[str, Sequence[str], None] = '7ee0940aea90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. Batch mode: SQLite can't ALTER TABLE to add a FK
    constraint directly -- batch mode does the copy-and-swap it needs."""
    with op.batch_alter_table('recommendations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('forecast_run_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_recommendations_forecast_run_id'), ['forecast_run_id'], unique=False)
        batch_op.create_foreign_key('fk_recommendations_forecast_run_id', 'forecast_runs', ['forecast_run_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('recommendations', schema=None) as batch_op:
        batch_op.drop_constraint('fk_recommendations_forecast_run_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_recommendations_forecast_run_id'))
        batch_op.drop_column('forecast_run_id')
