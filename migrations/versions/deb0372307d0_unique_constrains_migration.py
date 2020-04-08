"""unique constrains migration.

Revision ID: deb0372307d0
Revises: 0eece379b29d
Create Date: 2020-04-08 19:35:09.035233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'deb0372307d0'
down_revision = '0eece379b29d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_Genre_name'), 'Genre', ['name'], unique=True)
    op.create_index(op.f('ix_State_name'), 'State', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_State_name'), table_name='State')
    op.drop_index(op.f('ix_Genre_name'), table_name='Genre')
    # ### end Alembic commands ###
