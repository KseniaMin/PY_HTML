"""Add full_name, phone_number, travel_date, travel_time to Registration

Revision ID: 8e75d33810eb
Revises: 
Create Date: 2024-05-25 16:12:40.370913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e75d33810eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('registration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(length=100), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('phone_number', sa.String(length=20), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('travel_date', sa.Date(), nullable=False, server_default='1970-01-01'))
        batch_op.add_column(sa.Column('travel_time', sa.Time(), nullable=False, server_default='00:00:00'))

    # Удалите значения по умолчанию после добавления столбцов
    with op.batch_alter_table('registration', schema=None) as batch_op:
        batch_op.alter_column('full_name', server_default=None)
        batch_op.alter_column('phone_number', server_default=None)
        batch_op.alter_column('travel_date', server_default=None)
        batch_op.alter_column('travel_time', server_default=None)


def downgrade():
    with op.batch_alter_table('registration', schema=None) as batch_op:
        batch_op.drop_column('full_name')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('travel_date')
        batch_op.drop_column('travel_time')

    # ### end Alembic commands ###
