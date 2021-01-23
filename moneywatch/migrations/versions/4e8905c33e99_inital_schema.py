"""inital schema

Revision ID: 4e8905c33e99
Revises: 
Create Date: 2021-01-23 17:12:49.816432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e8905c33e99'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('iban', sa.String(length=22), nullable=False),
    sa.Column('balance', sa.Float(), nullable=False),
    sa.Column('color', sa.String(length=6), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_accounts')),
    sa.UniqueConstraint('iban', name=op.f('uq_accounts_iban')),
    sa.UniqueConstraint('name', name=op.f('uq_accounts_name'))
    )
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('type', sa.Enum('in', 'out'), nullable=False),
    sa.Column('budget_monthly', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('account_id', sa.Integer(), server_default='1', nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='fk_categories_account', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], name=op.f('fk_categories_parent_id_categories')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories'))
    )
    op.create_table('ruleset',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('pattern', sa.String(length=100), nullable=False),
    sa.Column('type', sa.Enum('in', 'out'), nullable=False),
    sa.Column('next_due', sa.Date(), nullable=True),
    sa.Column('next_valuta', sa.Float(), nullable=True),
    sa.Column('regular', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), server_default='1', nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='fk_rules_account', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_ruleset_category_id_categories')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ruleset'))
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('valuta', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('full_text', sa.String(length=100), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.Column('trend', sa.Float(), nullable=True),
    sa.Column('account_id', sa.Integer(), server_default='1', nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='fk_transactions_account', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_transactions_category'),
    sa.ForeignKeyConstraint(['rule_id'], ['ruleset.id'], name='fk_transactions_rule'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions'))
    )
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transactions_category_id'), ['category_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_rule_id'), ['rule_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_rule_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_date'))
        batch_op.drop_index(batch_op.f('ix_transactions_category_id'))

    op.drop_table('transactions')
    op.drop_table('ruleset')
    op.drop_table('categories')
    op.drop_table('accounts')
    # ### end Alembic commands ###
