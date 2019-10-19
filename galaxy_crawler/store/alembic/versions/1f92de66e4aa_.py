"""empty message

Revision ID: 1f92de66e4aa
Revises: 2ec47ac1328f
Create Date: 2019-10-19 16:59:02.784821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f92de66e4aa'
down_revision = '2ec47ac1328f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roles', 'import_branch')
    op.drop_column('roles', 'download_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('download_url', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
    op.add_column('roles', sa.Column('import_branch', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
