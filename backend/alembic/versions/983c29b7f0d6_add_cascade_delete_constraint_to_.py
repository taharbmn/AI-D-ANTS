"""Add CASCADE delete constraint to messages

Revision ID: 983c29b7f0d6
Revises:
Create Date: 2025-08-11 14:14:39.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '983c29b7f0d6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing foreign key constraint
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')

    # Add the new foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'messages_conversation_id_fkey',
        'messages', 'conversations',
        ['conversation_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Drop the CASCADE foreign key constraint
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')

    # Add back the original foreign key constraint without CASCADE
    op.create_foreign_key(
        'messages_conversation_id_fkey',
        'messages', 'conversations',
        ['conversation_id'], ['id']
    )
