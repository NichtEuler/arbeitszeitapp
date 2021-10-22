"""Create Message model

Revision ID: 0048e56aaa0a
Revises: 7198e8c48018
Create Date: 2021-10-22 20:33:55.825698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0048e56aaa0a'
down_revision = '7198e8c48018'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('sender', sa.String(), nullable=True),
    sa.Column('addressee', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('user_action', sa.Enum('answer_invite', name='useraction'), nullable=True),
    sa.Column('sender_remarks', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###
