"""empty message

Revision ID: 7ac5c41f311e
Revises: 
Create Date: 2023-03-12 20:40:48.503423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ac5c41f311e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chats',
    sa.Column('chat_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('type_', sa.Enum('private', 'group', 'supergroup', 'channel', name='chattype'), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('chat_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chats')
    # ### end Alembic commands ###
