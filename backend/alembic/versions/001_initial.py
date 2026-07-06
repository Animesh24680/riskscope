"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-30
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('age', sa.Float(), nullable=False),
        sa.Column('income', sa.Float(), nullable=False),
        sa.Column('credit_score', sa.Float(), nullable=False),
        sa.Column('missed_payments', sa.Integer(), nullable=False),
        sa.Column('debt_to_income_ratio', sa.Float(), nullable=False),
        sa.Column('is_delinquent', sa.Boolean(), nullable=False),
        sa.Column('risk_probability', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('top_risk_factor', sa.String(), nullable=True),
        sa.Column('method', sa.String(), default='ml_model'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('predictions')
