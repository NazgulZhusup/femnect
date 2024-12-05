"""Add details field to Project model

Revision ID: e70ad50f6e8b
Revises: <new_revision_id>
Create Date: 2024-12-02 21:19:34.540111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '070ad5076e8b'
down_revision = '3cd505195edb'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('project', sa.Column('details', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('project', 'details')