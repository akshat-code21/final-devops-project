from alembic import op
import sqlalchemy as sa


revision = "0002_create_expenses"
down_revision = "0001_create_tasks"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("category", sa.String(length=20), nullable=False, server_default="OTHER"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("paid_by", sa.String(length=120), nullable=False, server_default="Self"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_table("tasks")


def downgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="TODO"),
        sa.Column("assignee", sa.String(length=120), nullable=False, server_default="Unassigned"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_table("expenses")