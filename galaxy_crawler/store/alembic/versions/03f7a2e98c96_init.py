"""Init

Revision ID: 03f7a2e98c96
Revises: 
Create Date: 2019-07-21 00:45:25.873091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03f7a2e98c96'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('licenses',
    sa.Column('license_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('license_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('namespaces',
    sa.Column('namespace_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('company', sa.String(length=512), nullable=True),
    sa.Column('email', sa.String(length=512), nullable=True),
    sa.Column('location', sa.String(length=512), nullable=True),
    sa.Column('avatar_url', sa.String(length=512), nullable=True),
    sa.Column('html_url', sa.String(length=512), nullable=True),
    sa.Column('is_vendor', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('namespace_id')
    )
    op.create_index(op.f('ix_namespaces_name'), 'namespaces', ['name'], unique=True)
    op.create_table('platforms',
    sa.Column('platform_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('release', sa.String(length=512), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('platform_id'),
    sa.UniqueConstraint('name', 'release')
    )
    op.create_table('providers',
    sa.Column('provider_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('provider_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('role_types',
    sa.Column('role_type_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=8), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('role_type_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tags',
    sa.Column('tag_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('tag_id')
    )
    op.create_table('provider_namespaces',
    sa.Column('provider_namespace_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('display_name', sa.String(length=512), nullable=True),
    sa.Column('company', sa.String(length=512), nullable=True),
    sa.Column('email', sa.String(length=512), nullable=True),
    sa.Column('location', sa.String(length=512), nullable=True),
    sa.Column('avatar_url', sa.String(length=512), nullable=True),
    sa.Column('html_url', sa.String(length=512), nullable=True),
    sa.Column('followers_count', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('provider_id', sa.Integer(), nullable=True),
    sa.Column('namespace_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['namespace_id'], ['namespaces.namespace_id'], ),
    sa.ForeignKeyConstraint(['provider_id'], ['providers.provider_id'], ),
    sa.PrimaryKeyConstraint('provider_namespace_id'),
    sa.UniqueConstraint('provider_id', 'namespace_id')
    )
    op.create_index(op.f('ix_provider_namespaces_name'), 'provider_namespaces', ['name'], unique=True)
    op.create_table('repositories',
    sa.Column('repository_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('readme', sa.Text(), nullable=True),
    sa.Column('readme_html', sa.Text(), nullable=True),
    sa.Column('clone_url', sa.String(length=512), nullable=True),
    sa.Column('issue_tracker_url', sa.String(length=512), nullable=True),
    sa.Column('external_url', sa.String(length=512), nullable=True),
    sa.Column('commit', sa.String(length=512), nullable=True),
    sa.Column('commit_url', sa.String(length=512), nullable=True),
    sa.Column('commit_message', sa.Text(), nullable=True),
    sa.Column('commit_created', sa.DateTime(), nullable=True),
    sa.Column('travis_build_url', sa.String(length=512), nullable=True),
    sa.Column('travis_status_url', sa.String(length=512), nullable=True),
    sa.Column('stargazers_count', sa.Integer(), nullable=True),
    sa.Column('watchers_count', sa.Integer(), nullable=True),
    sa.Column('forks_count', sa.Integer(), nullable=True),
    sa.Column('open_issues_count', sa.Integer(), nullable=True),
    sa.Column('community_score', sa.Integer(), nullable=True),
    sa.Column('community_survey_count', sa.Integer(), nullable=True),
    sa.Column('quality_score', sa.Integer(), nullable=True),
    sa.Column('quality_score_date', sa.DateTime(), nullable=True),
    sa.Column('deprecated', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('provider_namespace_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['provider_namespace_id'], ['provider_namespaces.provider_namespace_id'], ),
    sa.PrimaryKeyConstraint('repository_id'),
    sa.UniqueConstraint('name', 'provider_namespace_id')
    )
    op.create_table('roles',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('role_type', sa.Integer(), nullable=True),
    sa.Column('namespace', sa.Integer(), nullable=True),
    sa.Column('repository', sa.Integer(), nullable=True),
    sa.Column('min_ansible_version', sa.String(length=10), nullable=True),
    sa.Column('download_count', sa.Integer(), nullable=True),
    sa.Column('download_url', sa.String(length=512), nullable=True),
    sa.Column('import_branch', sa.String(length=512), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('deprecated', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['namespace'], ['namespaces.namespace_id'], ),
    sa.ForeignKeyConstraint(['repository'], ['repositories.repository_id'], ),
    sa.ForeignKeyConstraint(['role_type'], ['role_types.role_type_id'], ),
    sa.PrimaryKeyConstraint('role_id'),
    sa.UniqueConstraint('name', 'namespace')
    )
    op.create_table('license_statuses',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('license_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['license_id'], ['licenses.license_id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('role_id', 'license_id')
    )
    op.create_table('platform_statuses',
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['platform_id'], ['platforms.platform_id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('platform_id', 'role_id')
    )
    op.create_table('role_dependencies',
    sa.Column('from_id', sa.Integer(), nullable=False),
    sa.Column('to_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['roles.role_id'], ),
    sa.ForeignKeyConstraint(['to_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('from_id', 'to_id')
    )
    op.create_table('role_versions',
    sa.Column('version_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('repository', sa.Integer(), nullable=True),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.Column('release_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['repository'], ['repositories.repository_id'], ),
    sa.ForeignKeyConstraint(['role'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('version_id'),
    sa.UniqueConstraint('name', 'repository')
    )
    op.create_table('tags_association',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.tag_id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'role_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags_association')
    op.drop_table('role_versions')
    op.drop_table('role_dependencies')
    op.drop_table('platform_statuses')
    op.drop_table('license_statuses')
    op.drop_table('roles')
    op.drop_table('repositories')
    op.drop_index(op.f('ix_provider_namespaces_name'), table_name='provider_namespaces')
    op.drop_table('provider_namespaces')
    op.drop_table('tags')
    op.drop_table('role_types')
    op.drop_table('providers')
    op.drop_table('platforms')
    op.drop_index(op.f('ix_namespaces_name'), table_name='namespaces')
    op.drop_table('namespaces')
    op.drop_table('licenses')
    # ### end Alembic commands ###
