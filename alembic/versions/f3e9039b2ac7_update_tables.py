"""update tables

Revision ID: f3e9039b2ac7
Revises: 5ea1b3435530
Create Date: 2025-03-22 17:58:27.273630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3e9039b2ac7'
down_revision: Union[str, None] = '5ea1b3435530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('links', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'links', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'links', type_='foreignkey')
    op.drop_column('links', 'user_id')
    # ### end Alembic commands ###
