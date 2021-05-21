"""
Definition of database tables.
"""

from flask_login import UserMixin
from sqlalchemy.orm import backref
from project.extensions import db


# Association table Company - Member
jobs = db.Table(
    "jobs",
    db.Column("member_id", db.Integer, db.ForeignKey("member.id")),
    db.Column("company_id", db.Integer, db.ForeignKey("company.id"))
)


class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    guthaben = db.Column(db.Numeric(), default=0, nullable=False)

    workplaces = db.relationship(
        "Company",
        secondary=jobs,
        lazy="dynamic",
        backref=db.backref("workers", lazy="dynamic")
        )
        
        
class Company(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    guthaben = db.Column(db.Numeric(), default=0)
    fik = db.Column(db.Numeric(), nullable=False, default=1)

    plans = db.relationship(
        "Plan", lazy=True, backref="company"
    )

    def __repr__(self):
        return "<Company(email='%s', name='%s', guthaben='%s', fik='%s')>" % (
                             self.email, self.name, self.guthaben, self.fik)


class Plan(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_creation_date = db.Column(db.DateTime, nullable=False)
    planner = db.Column(
        db.Integer, db.ForeignKey("company.id"), nullable=False)
    costs_p = db.Column(db.Numeric(), nullable=False)
    costs_r = db.Column(db.Numeric(), nullable=False)
    costs_a = db.Column(db.Numeric(), nullable=False)
    prd_name = db.Column(db.String(100), nullable=False)
    prd_unit = db.Column(db.String(20), nullable=False)
    prd_amount = db.Column(db.Numeric(), nullable=False) 
    description = db.Column(db.String(2000), nullable=False)
    timeframe = db.Column(db.Numeric(), nullable=False)


class Angebote(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cr_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    company = db.Column(
        db.Integer, db.ForeignKey("company.id"), nullable=False)
    beschreibung = db.Column(db.String(1000), nullable=False)
    kategorie = db.Column(db.String(50), nullable=False)
    p_kosten = db.Column(db.Numeric(), nullable=False)
    v_kosten = db.Column(db.Numeric(), nullable=False)
    preis = db.Column(db.Numeric(), nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<Angebote(cr_date='%s', name='%s', company='%s', \
beschreibung='%s', kategorie='%s', \
p_kosten='%s', v_kosten='%s', preis='%s', aktiv='%s')>" % (
                             self.cr_date, self.name, self.company,
                             self.beschreibung,
                             self.kategorie, self.p_kosten, self.v_kosten,
                             self.preis, self.aktiv)


class Kaeufe(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kauf_date = db.Column(db.DateTime, nullable=False)
    angebot = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    type_member = db.Column(db.Boolean, nullable=False)
    company = db.Column(
        db.Integer, db.ForeignKey("company.id"), nullable=True)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=True)
    kaufpreis = db.Column(db.Numeric(), nullable=False)


class Arbeit(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    stunden = db.Column(db.Numeric(), nullable=False)
    # ausbezahlt = db.Column(db.Boolean, nullable=False, default=False)


class Produktionsmittel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    kauf = db.Column(db.Integer, db.ForeignKey("kaeufe.id"), nullable=False)
    prozent_gebraucht = db.Column(db.Numeric(), nullable=False)

    def __repr__(self):
        return "<Produktionsmittel(angebot='%s', kauf='%s', \
prozent_gebraucht='%s')>" % (
                             self.angebot, self.kauf, self.prozent_gebraucht)


class Withdrawal(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_member = db.Column(db.Boolean, nullable=False)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    betrag = db.Column(db.Numeric(), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    entwertet = db.Column(db.Boolean, nullable=False, default=False)


class Kooperationen(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cr_date = db.Column(db.DateTime, nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)


class KooperationenMitglieder(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kooperation = db.Column(
        db.Integer, db.ForeignKey("kooperationen.id"), nullable=False)
    mitglied = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)
