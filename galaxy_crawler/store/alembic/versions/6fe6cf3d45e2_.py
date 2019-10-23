"""empty message

Revision ID: 6fe6cf3d45e2
Revises: 1f92de66e4aa
Create Date: 2019-10-22 22:37:18.855253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fe6cf3d45e2'
down_revision = '1f92de66e4aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('role_versions_name_repository_key', 'role_versions', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('role_versions_name_repository_key', 'role_versions', ['name', 'repository'])
    # ### end Alembic commands ###
