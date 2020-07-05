"""change category_id can be NULL

Revision ID: 07f9fee4d16a
Revises: 8a1bd376774f
Create Date: 2020-01-27 21:11:39.738302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07f9fee4d16a'
down_revision = '8a1bd376774f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('category_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('category_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###