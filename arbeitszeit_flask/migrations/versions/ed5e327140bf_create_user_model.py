"""Create User model

Revision ID: ed5e327140bf
Revises: ddb975a7f24b
Create Date: 2022-06-25 15:07:35.943812

"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = "ed5e327140bf"
down_revision = "ddb975a7f24b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    users_table = op.create_table(
        "user",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.add_column("accountant", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key(None, "accountant", "user", ["user_id"], ["id"])
    op.add_column("company", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key(None, "company", "user", ["user_id"], ["id"])
    op.add_column("member", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key(None, "member", "user", ["user_id"], ["id"])
    # ### end Alembic commands ###
    connection = op.get_bind()
    migrator = ForwardMigrator(connection, users_table)
    migrator.copy_accountant_credentials()
    migrator.copy_company_credentials()
    migrator.copy_member_credentials()
    op.alter_column('accountant', 'user_id', nullable=False)
    op.alter_column('member', 'user_id', nullable=False)
    op.alter_column('company', 'user_id', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("member_user_id_fkey", "member", type_="foreignkey")
    op.drop_column("member", "user_id")
    op.drop_constraint("company_user_id_fkey", "company", type_="foreignkey")
    op.drop_column("company", "user_id")
    op.drop_constraint("accountant_user_id_fkey", "accountant", type_="foreignkey")
    op.drop_column("accountant", "user_id")
    op.drop_table("user")
    # ### end Alembic commands ###


class ForwardMigrator:
    members = sa.Table(
        "member",
        sa.MetaData(),
        sa.Column("id", sa.String()),
        sa.Column("email", sa.String()),
        sa.Column("password", sa.String()),
        sa.Column("user_id", sa.String()),
    )
    companies = sa.Table(
        "company",
        sa.MetaData(),
        sa.Column("id", sa.String()),
        sa.Column("email", sa.String()),
        sa.Column("password", sa.String()),
        sa.Column("user_id", sa.String()),
    )
    accountants = sa.Table(
        "accountant",
        sa.MetaData(),
        sa.Column("id", sa.String()),
        sa.Column("email", sa.String()),
        sa.Column("password", sa.String()),
        sa.Column("user_id", sa.String()),
    )

    def __init__(self, connection, users_table):
        self.connection = connection
        self.users = users_table

    def copy_member_credentials(self):
        for member in self._fetch_user_credentials(self.members):
            user_id = self._insert_or_skip_user(credentials=member)
            self._point_to_user(id=member["id"], user_id=user_id, table=self.members)

    def copy_company_credentials(self):
        for company in self._fetch_user_credentials(self.companies):
            user_id = self._insert_or_skip_user(credentials=company)
            self._point_to_user(id=company["id"], user_id=user_id, table=self.companies)

    def copy_accountant_credentials(self):
        for accountant in self._fetch_user_credentials(self.accountants):
            user_id = self._insert_or_skip_user(credentials=accountant)
            self._point_to_user(
                id=accountant["id"], user_id=user_id, table=self.accountants
            )

    def _fetch_user_credentials(self, table):
        for id_, email, password in self.connection.execute(
            sa.select(
                [
                    table.c.id,
                    table.c.email,
                    table.c.password,
                ]
            )
        ).fetchall():
            yield {
                "id": id_,
                "email": email,
                "password": password,
            }

    def _insert_or_skip_user(self, credentials):
        """Insert a new user. If a user with credentials['email']
        already exists, do nothing.

        Return the id of the user matching the credentials['email']
        """
        select_statement = sa.select(
            self.users.c.id,
            self.users.c.email,
        ).where(self.users.c.email == credentials["email"])
        result = self.connection.execute(select_statement).fetchone()
        if result:
            return result[0]
        else:
            user_uuid = str(uuid4())
            self.connection.execute(
                sa.insert(self.users).values(
                    id=user_uuid,
                    email=credentials["email"],
                    password=credentials["password"],
                )
            )
            return user_uuid

    def _point_to_user(self, *, id, user_id, table):
        self.connection.execute(
            table.update().values(dict(user_id=user_id)).where(table.c.id == id)
        )
