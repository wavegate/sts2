"""run-key

Revision ID: f5158048830d
Revises: 783c776753a8
Create Date: 2026-03-08 09:13:27.858011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5158048830d'
down_revision: Union[str, Sequence[str], None] = '783c776753a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Switch runs from id PK to composite (start_time, seed) PK."""
    op.execute(sa.text("DROP INDEX IF EXISTS ix_runs_build_id"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_runs_character"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_runs_game_mode"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_runs_killed_by_encounter"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_runs_seed"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_runs_start_time"))
    op.execute(sa.text("ALTER TABLE runs DROP COLUMN IF EXISTS id"))
    op.create_primary_key("runs_pkey", "runs", ["start_time", "seed"])


def downgrade() -> None:
    """Revert to single id PK."""
    op.drop_constraint("runs_pkey", "runs", type_="primary")
    op.add_column('runs', sa.Column('id', sa.INTEGER(),
                  autoincrement=True, nullable=False))
    op.create_primary_key("runs_pkey", "runs", ["id"])
    op.create_index(op.f('ix_runs_start_time'), 'runs',
                    ['start_time'], unique=False)
    op.create_index(op.f('ix_runs_seed'), 'runs', ['seed'], unique=False)
    op.create_index(op.f('ix_runs_killed_by_encounter'), 'runs', [
                    'killed_by_encounter'], unique=False)
    op.create_index(op.f('ix_runs_game_mode'), 'runs',
                    ['game_mode'], unique=False)
    op.create_index(op.f('ix_runs_character'), 'runs',
                    ['character'], unique=False)
    op.create_index(op.f('ix_runs_build_id'), 'runs',
                    ['build_id'], unique=False)
