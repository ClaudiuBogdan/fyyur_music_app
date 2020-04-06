"""add column website to venue artist migration.

Revision ID: 6d20c279f5aa
Revises: 9fb0bd749112
Create Date: 2020-04-06 12:58:08.704317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d20c279f5aa'
down_revision = '9fb0bd749112'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###