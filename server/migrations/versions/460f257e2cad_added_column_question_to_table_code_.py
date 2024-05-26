"""Added column question to table code results

Revision ID: 460f257e2cad
Revises: a43b2b961ea7
Create Date: 2024-05-26 17:08:35.373615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '460f257e2cad'
down_revision = 'a43b2b961ea7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('code_results', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('code_results', schema=None) as batch_op:
        batch_op.drop_column('question')

    # ### end Alembic commands ###