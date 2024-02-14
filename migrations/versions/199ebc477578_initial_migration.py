"""Initial migration.

Revision ID: 199ebc477578
Revises: 
Create Date: 2024-02-14 16:47:50.927239

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '199ebc477578'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(length=255), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('_password',
               existing_type=mysql.VARCHAR(length=500),
               type_=sa.Text(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('_password',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=500),
               nullable=True)

    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_column('image')

    # ### end Alembic commands ###