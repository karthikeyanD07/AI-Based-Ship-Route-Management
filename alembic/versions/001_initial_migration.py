"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-02 19:51:00.000000

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ships table
    op.create_table(
        'ships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mmsi', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('sog', sa.Float(), nullable=True),
        sa.Column('cog', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=100), nullable=True),
        sa.Column('position', Geometry('POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ships_mmsi'), 'ships', ['mmsi'], unique=True)
    op.create_index(op.f('ix_ships_id'), 'ships', ['id'], unique=False)
    
    # Create routes table
    op.create_table(
        'routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ship_id', sa.String(length=100), nullable=False),
        sa.Column('start_port', sa.String(length=255), nullable=False),
        sa.Column('end_port', sa.String(length=255), nullable=False),
        sa.Column('route_points', sa.Text(), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('estimated_time_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)
    op.create_index(op.f('ix_routes_ship_id'), 'routes', ['ship_id'], unique=False)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('roles', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource', sa.String(length=255), nullable=True),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_username'), 'audit_logs', ['username'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_request_id'), 'audit_logs', ['request_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_request_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_username'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_routes_ship_id'), table_name='routes')
    op.drop_index(op.f('ix_routes_id'), table_name='routes')
    op.drop_table('routes')
    
    op.drop_index(op.f('ix_ships_id'), table_name='ships')
    op.drop_index(op.f('ix_ships_mmsi'), table_name='ships')
    op.drop_table('ships')
