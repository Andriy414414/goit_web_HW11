"""Init

Revision ID: 086cd2c659dd
Revises: 
Create Date: 2023-12-10 19:55:06.750518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '086cd2c659dd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('todos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('second_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('birthday', sa.DateTime(), nullable=False),
    sa.Column('add_info', sa.String(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_todos_email'), 'todos', ['email'], unique=False)
    op.create_index(op.f('ix_todos_first_name'), 'todos', ['first_name'], unique=False)
    op.create_index(op.f('ix_todos_second_name'), 'todos', ['second_name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_todos_second_name'), table_name='todos')
    op.drop_index(op.f('ix_todos_first_name'), table_name='todos')
    op.drop_index(op.f('ix_todos_email'), table_name='todos')
    op.drop_table('todos')
    # ### end Alembic commands ###
