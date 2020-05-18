"""empty message

Revision ID: 374c230062df
Revises: 
Create Date: 2020-05-18 00:56:54.001938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '374c230062df'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_manager',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('osm_id', sa.Integer(), nullable=False),
    sa.Column('task_manager', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_manager'], ['task_manager.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link', sa.String(length=200), nullable=True),
    sa.Column('commit_hash', sa.String(length=500), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('document')
    op.drop_table('user')
    op.drop_table('task_manager')
    # ### end Alembic commands ###
