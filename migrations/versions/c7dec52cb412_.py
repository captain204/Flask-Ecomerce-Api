"""empty message

Revision ID: c7dec52cb412
Revises: 
Create Date: 2020-05-04 15:01:43.186929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7dec52cb412'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.String(length=250), nullable=False),
    sa.Column('product', sa.String(length=250), nullable=False),
    sa.Column('price', sa.String(length=250), nullable=False),
    sa.Column('description', sa.String(length=250), nullable=False),
    sa.Column('fullname', sa.String(length=250), nullable=False),
    sa.Column('address', sa.String(length=250), nullable=False),
    sa.Column('shipping_type', sa.String(length=250), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password_hash', sa.String(length=120), nullable=False),
    sa.Column('creation_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=250), nullable=False),
    sa.Column('product_category_id', sa.Integer(), nullable=False),
    sa.Column('tags', sa.String(length=250), nullable=False),
    sa.Column('creation_date', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['product_category_id'], ['product_category.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product')
    op.drop_table('user')
    op.drop_table('product_category')
    op.drop_table('order')
    # ### end Alembic commands ###