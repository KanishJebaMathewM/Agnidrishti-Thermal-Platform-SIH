"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create spatial extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Table: authorities
    op.create_table(
        'authorities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('authority_type', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('official_email', sa.String(length=200), nullable=False),
        sa.Column('official_phone', sa.String(length=20), nullable=True),
        sa.Column('portal_url', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('verified_on', sa.Date(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_authorities_state', 'authorities', ['state'])
    op.create_index('ix_authorities_district', 'authorities', ['district'])

    # Table: routing_profiles
    op.create_table(
        'routing_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('classification', sa.String(length=50), nullable=False),
        sa.Column('primary_authority_id', sa.UUID(), nullable=False),
        sa.Column('secondary_authority_ids', postgresql.ARRAY(sa.UUID()), nullable=True),
        sa.Column('rules', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['primary_authority_id'], ['authorities.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_routing_profiles_state', 'routing_profiles', ['state'])
    op.create_index('ix_routing_profiles_district', 'routing_profiles', ['district'])

    # Table: thermal_sources
    op.create_table(
        'thermal_sources',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('h3_cell', sa.String(length=15), nullable=False),
        sa.Column('representative_lat', sa.Float(), nullable=False),
        sa.Column('representative_lon', sa.Float(), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('first_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('observation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expected_class', sa.String(length=50), nullable=True),
        sa.Column('mean_frp', sa.Float(), nullable=True),
        sa.Column('frp_std', sa.Float(), nullable=True),
        sa.Column('median_frp', sa.Float(), nullable=True),
        sa.Column('monthly_profile', sa.JSON(), nullable=True),
        sa.Column('seasonal_profile', sa.JSON(), nullable=True),
        sa.Column('typical_hours', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='NEW'),
        sa.Column('classification_confidence', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('h3_cell')
    )
    op.create_index('ix_thermal_sources_h3_cell', 'thermal_sources', ['h3_cell'])
    op.create_index('ix_thermal_sources_state', 'thermal_sources', ['state'])
    op.create_index('ix_thermal_sources_district', 'thermal_sources', ['district'])

    # Table: observations
    op.create_table(
        'observations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('source_product', sa.String(length=50), nullable=True),
        sa.Column('satellite', sa.String(length=50), nullable=True),
        sa.Column('timestamp_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('h3_cell', sa.String(length=15), nullable=True),
        sa.Column('frp', sa.Float(), nullable=True),
        sa.Column('bright_ti4', sa.Float(), nullable=True),
        sa.Column('bright_ti5', sa.Float(), nullable=True),
        sa.Column('confidence', sa.String(length=10), nullable=True),
        sa.Column('quality_flags', sa.JSON(), nullable=True),
        sa.Column('thermal_features', sa.JSON(), nullable=True),
        sa.Column('raw_record_ref', sa.JSON(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('source_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['thermal_sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_observations_timestamp_utc', 'observations', ['timestamp_utc'])
    op.create_index('ix_observations_h3_cell', 'observations', ['h3_cell'])

    # Table: events
    op.create_table(
        'events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('first_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('centroid_lat', sa.Float(), nullable=False),
        sa.Column('centroid_lon', sa.Float(), nullable=False),
        sa.Column('centroid', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='centroid'), nullable=False),
        sa.Column('observation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('source_id', sa.UUID(), nullable=True),
        sa.Column('classification', sa.String(length=50), nullable=False),
        sa.Column('classification_confidence', sa.Float(), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('anomaly_flag', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='NORMAL'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='NEW'),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['source_id'], ['thermal_sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Table: event_observations
    op.create_table(
        'event_observations',
        sa.Column('event_id', sa.UUID(), nullable=False),
        sa.Column('observation_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['observation_id'], ['observations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'observation_id')
    )

    # Table: notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.UUID(), nullable=False),
        sa.Column('authority_id', sa.UUID(), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='READY'),
        sa.Column('alert_content', sa.JSON(), nullable=True),
        sa.Column('presented_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_taken_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('operator_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['authority_id'], ['authorities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Table: operator_feedback
    op.create_table(
        'operator_feedback',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.UUID(), nullable=False),
        sa.Column('model_prediction', sa.String(length=50), nullable=True),
        sa.Column('model_confidence', sa.Float(), nullable=True),
        sa.Column('human_label', sa.String(length=50), nullable=False),
        sa.Column('reviewer', sa.String(length=100), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Table: admin_boundaries
    op.create_table(
        'admin_boundaries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('state_id', sa.String(length=50), nullable=True),
        sa.Column('state_name', sa.String(length=100), nullable=True),
        sa.Column('district_id', sa.String(length=50), nullable=True),
        sa.Column('district_name', sa.String(length=100), nullable=True),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_admin_boundaries_state_id', 'admin_boundaries', ['state_id'])
    op.create_index('ix_admin_boundaries_state_name', 'admin_boundaries', ['state_name'])
    op.create_index('ix_admin_boundaries_district_id', 'admin_boundaries', ['district_id'])
    op.create_index('ix_admin_boundaries_district_name', 'admin_boundaries', ['district_name'])

    # Table: industrial_facilities
    op.create_table(
        'industrial_facilities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('facility_type', sa.String(length=50), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('osm_id', sa.BigInteger(), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Table: landuse_features
    op.create_table(
        'landuse_features',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('class', sa.String(length=50), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Table: forest_boundaries
    op.create_table(
        'forest_boundaries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Table: model_versions
    op.create_table(
        'model_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('version_tag', sa.String(length=50), nullable=False),
        sa.Column('feature_set_version', sa.String(length=50), nullable=True),
        sa.Column('training_data_version', sa.String(length=50), nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('artifact_path', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_tag')
    )
    op.create_index('ix_model_versions_version_tag', 'model_versions', ['version_tag'])

    # Table: training_labels
    op.create_table(
        'training_labels',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('observation_id', sa.UUID(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('label_source', sa.String(length=100), nullable=True),
        sa.Column('label_confidence', sa.Float(), nullable=True),
        sa.Column('verification_status', sa.String(length=30), nullable=False, server_default='UNVERIFIED'),
        sa.Column('labeled_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['observation_id'], ['observations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('training_labels')
    op.drop_index('ix_model_versions_version_tag', table_name='model_versions')
    op.drop_table('model_versions')
    op.drop_table('forest_boundaries')
    op.drop_table('landuse_features')
    op.drop_table('industrial_facilities')
    op.drop_index('ix_admin_boundaries_district_name', table_name='admin_boundaries')
    op.drop_index('ix_admin_boundaries_district_id', table_name='admin_boundaries')
    op.drop_index('ix_admin_boundaries_state_name', table_name='admin_boundaries')
    op.drop_index('ix_admin_boundaries_state_id', table_name='admin_boundaries')
    op.drop_table('admin_boundaries')
    op.drop_table('operator_feedback')
    op.drop_table('notifications')
    op.drop_table('event_observations')
    op.drop_table('events')
    op.drop_index('ix_observations_h3_cell', table_name='observations')
    op.drop_index('ix_observations_timestamp_utc', table_name='observations')
    op.drop_table('observations')
    op.drop_index('ix_thermal_sources_h3_cell', table_name='thermal_sources')
    op.drop_index('ix_thermal_sources_district', table_name='thermal_sources')
    op.drop_index('ix_thermal_sources_state', table_name='thermal_sources')
    op.drop_table('thermal_sources')
    op.drop_index('ix_routing_profiles_district', table_name='routing_profiles')
    op.drop_index('ix_routing_profiles_state', table_name='routing_profiles')
    op.drop_table('routing_profiles')
    op.drop_index('ix_authorities_district', table_name='authorities')
    op.drop_index('ix_authorities_state', table_name='authorities')
    op.drop_table('authorities')
    
    op.execute("DROP EXTENSION IF EXISTS postgis")
