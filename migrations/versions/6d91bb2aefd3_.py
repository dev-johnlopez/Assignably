"""empty message

Revision ID: 6d91bb2aefd3
Revises: 
Create Date: 2019-06-01 10:35:18.132580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d91bb2aefd3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line_1', sa.String(length=255), nullable=True),
    sa.Column('line_2', sa.String(length=255), nullable=True),
    sa.Column('line_3', sa.String(length=255), nullable=True),
    sa.Column('line_4', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=True),
    sa.Column('state_code', sa.String(length=2), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.Column('county', sa.String(length=255), nullable=True),
    sa.Column('country', sa.String(length=255), nullable=True),
    sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True),
    sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('api_key', sa.String(length=255), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('current_login_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_ip', sa.String(length=40), nullable=True),
    sa.Column('current_login_ip', sa.String(length=40), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_api_key'), 'user', ['api_key'], unique=True)
    op.create_table('contact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('property_tax', sa.Integer(), nullable=True),
    sa.Column('sq_feet', sa.Integer(), nullable=True),
    sa.Column('bedrooms', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Integer(), nullable=True),
    sa.Column('after_repair_value', sa.Integer(), nullable=True),
    sa.Column('rehab_estimate', sa.Integer(), nullable=True),
    sa.Column('purchase_price', sa.Integer(), nullable=True),
    sa.Column('list_price', sa.Integer(), nullable=True),
    sa.Column('under_contract_ind', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['address.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('partnership_email_recipient', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('partnership_email_recipient')
    )
    op.create_table('deal_contact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deal_id', sa.Integer(), nullable=True),
    sa.Column('contact_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['contact_id'], ['contact.id'], ),
    sa.ForeignKeyConstraint(['deal_id'], ['deal.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deal_contact_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('deal_contact_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['deal_contact_id'], ['deal_contact.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('deal_contact_role')
    op.drop_table('deal_contact')
    op.drop_table('settings')
    op.drop_table('roles_users')
    op.drop_table('deal')
    op.drop_table('contact')
    op.drop_index(op.f('ix_user_api_key'), table_name='user')
    op.drop_table('user')
    op.drop_table('role')
    op.drop_table('address')
    # ### end Alembic commands ###
