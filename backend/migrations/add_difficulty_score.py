"""Add difficulty_score to questions table

Revision ID: add_difficulty_score_001
Revises: 
Create Date: 2025-06-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_difficulty_score_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add difficulty_score column to questions table
    op.add_column('questions', sa.Column('difficulty_score', sa.Float(), nullable=True, default=0.0))
    
    # Update existing records to have a default difficulty_score based on difficulty_level
    connection = op.get_bind()
    
    # Map difficulty levels to IRT scores
    connection.execute("""
        UPDATE questions 
        SET difficulty_score = CASE 
            WHEN difficulty_level = 'easy' THEN -1.0
            WHEN difficulty_level = 'medium' THEN 0.0
            WHEN difficulty_level = 'hard' THEN 1.0
            ELSE 0.0
        END
        WHERE difficulty_score IS NULL
    """)
    
    # Make column non-nullable after setting defaults
    op.alter_column('questions', 'difficulty_score',
                    existing_type=sa.Float(),
                    nullable=False,
                    server_default='0.0')


def downgrade():
    # Remove difficulty_score column
    op.drop_column('questions', 'difficulty_score')