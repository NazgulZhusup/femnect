"""Merge migrations

Revision ID: de9189a73d80
Revises: 80f08d9de429, 070ad5076e8b
Create Date: 2024-12-02 21:50:04.049661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de9189a73d80'
down_revision = ('070ad5076e8b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
