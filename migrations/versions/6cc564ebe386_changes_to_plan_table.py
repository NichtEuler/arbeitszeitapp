"""changes to plan table

Revision ID: 6cc564ebe386
Revises: 7198e8c48018
Create Date: 2021-10-20 01:00:11.567667

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6cc564ebe386"
down_revision = "7198e8c48018"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plan", sa.Column("active_days", sa.Integer(), nullable=True))
    # the following calculation of active_days will work with postgres, not with sqlite
    # (because of the DATE_PART function.)
    # this update-statement is equivalent to the _calculate_active_days() in Use Case UpdatePlansAndPayout
    op.execute(
        """
    UPDATE plan SET active_days = 
        CASE
            WHEN timeframe < DATE_PART('day', now() - activation_date) THEN timeframe
            ELSE DATE_PART('day', now() - activation_date) 
        END
    where is_active
    """
    )

    # the payout_count can only be calculated from the active_days column.
    # there is no guarantee that this calculation of payout_count is in fact correct
    # because it might be that payouts have been skipped in the past
    op.add_column("plan", sa.Column("payout_count", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE plan SET payout_count = 
            CASE
                WHEN active_days IS NOT NULL THEN active_days + 1
                ELSE 0
            END
        """
    )
    op.alter_column("plan", "payout_count", nullable=False)

    op.drop_column("plan", "last_certificate_payout")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "plan",
        sa.Column(
            "last_certificate_payout",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("plan", "payout_count")
    op.drop_column("plan", "active_days")
    # ### end Alembic commands ###
