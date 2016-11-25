from datetime import datetime
from alembic import op
import sqlalchemy as sa

"""empty message

Revision ID: f76b1fb88978
Revises: None
Create Date: 2016-11-25 15:30:34.024225

"""

# revision identifiers, used by Alembic.
revision = 'f76b1fb88978'
down_revision = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.Text, nullable=False),
        sa.Column('pasword_hash', sa.Text),
        sa.Column('inserted_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'))

    op.create_table(
        'albums',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Integer),
        sa.Column('user_id', sa.Integer),
        sa.Column('inserted_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']))

    op.create_table(
        'photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text),
        sa.Column('file_name', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Integer),
        sa.Column('album_id', sa.Integer),
        sa.Column('inserted_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['album_id'], ['albums.id']))


def downgrade():
    op.drop_table('photos')
    op.drop_table('albums')
    op.drop_table('users')
