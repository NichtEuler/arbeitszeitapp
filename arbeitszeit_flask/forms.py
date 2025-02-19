from decimal import Decimal
from typing import Generic, TypeVar

from wtforms import (
    BooleanField,
    DecimalField,
    Form,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)

from .translator import FlaskTranslator

T = TypeVar("T")


class WtFormField(Generic[T]):
    def __init__(self, form: Form, field_name: str) -> None:
        self._form = form
        self._field_name = field_name

    def get_value(self) -> T:
        return self._form.data[self._field_name]

    def attach_error(self, message: str) -> None:
        self._field.errors.append(message)

    def set_value(self, value: T) -> None:
        self._field.data = value

    @property
    def _field(self):
        return getattr(self._form, self._field_name)


trans = FlaskTranslator()

error_msgs = {
    "uuid": trans.lazy_gettext("Invalid ID."),
    "num_range_min_0": trans.lazy_gettext("Number must be at least 0."),
}


class FieldMustExist:
    def __init__(self, message: str) -> None:
        self.message = message

    def __call__(self, form, field):
        if not self._field_has_data(field):
            if self.message is None:
                message = field.gettext("This field is required.")
            else:
                message = self.message

            field.errors[:] = []
            raise validators.StopValidation(message)

    def _field_has_data(self, field):
        return field.raw_data


class PlanSearchForm(Form):
    choices = [
        ("Plan-ID", trans.lazy_gettext("Plan ID")),
        ("Produktname", trans.lazy_gettext("Product name")),
    ]
    select = SelectField(
        trans.lazy_gettext("Search Plans"),
        choices=choices,
        validators=[validators.DataRequired()],
    )
    search = StringField(
        trans.lazy_gettext("Search term"),
        validators=[
            FieldMustExist(message=trans.lazy_gettext("Required")),
        ],
    )

    choices_radio = [
        ("activation", trans.lazy_gettext("Newest")),
        ("company_name", trans.lazy_gettext("Company name")),
        ("price", trans.lazy_gettext("Lowest cost")),
    ]
    radio = RadioField(
        choices=choices_radio,
        default="activation",
        validators=[FieldMustExist(message=trans.lazy_gettext("Required"))],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]

    def get_radio_string(self) -> str:
        return self.data["radio"]


class RegisterForm(Form):
    email = StringField(
        trans.lazy_gettext("Email"),
        validators=[
            validators.Email(
                message=trans.lazy_gettext("Proper email address required")
            )
        ],
    )
    name = StringField(
        trans.lazy_gettext("Name"),
        validators=[validators.InputRequired(message="Name is required")],
    )
    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.Length(
                min=8,
                message=trans.lazy_gettext(
                    "The password must be at least 8 characters in length"
                ),
            )
        ],
    )

    def get_email_string(self) -> str:
        return self.data["email"]

    def get_name_string(self) -> str:
        return self.data["name"]

    def get_password_string(self) -> str:
        return self.data["password"]

    def add_email_error(self, error: str) -> None:
        self.email.errors.append(error)


class RegisterAccountantForm(Form):
    email = StringField(
        trans.lazy_gettext("Email"),
        validators=[
            validators.InputRequired(
                message=trans.lazy_gettext("Email address is required")
            )
        ],
    )
    name = StringField(
        trans.lazy_gettext("Name"),
        validators=[
            validators.InputRequired(message=trans.lazy_gettext("Name is required"))
        ],
    )
    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.Length(
                min=8,
                message=trans.lazy_gettext(
                    "The password must be at least 8 characters in length"
                ),
            )
        ],
    )

    def get_email_address(self) -> str:
        return self.data["email"]

    def get_name(self) -> str:
        return self.data["name"]

    def get_password(self) -> str:
        return self.data["password"]


class LoginForm(Form):
    email = StringField(
        trans.lazy_gettext("Email"),
        validators=[
            validators.InputRequired(
                message=trans.lazy_gettext("Email address required")
            )
        ],
    )

    password = PasswordField(
        trans.lazy_gettext("Password"),
        validators=[
            validators.InputRequired(message=trans.lazy_gettext("Password is required"))
        ],
    )
    remember = BooleanField(trans.lazy_gettext("Remember login?"))

    def email_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="email")

    def password_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="password")

    def remember_field(self) -> WtFormField[bool]:
        return WtFormField(form=self, field_name="remember")


class PayConsumerProductForm(Form):
    plan_id = StringField(
        trans.lazy_gettext("Plan ID"),
        render_kw={"placeholder": trans.lazy_gettext("Plan ID")},
        validators=[
            validators.InputRequired(),
        ],
    )
    amount = StringField(
        trans.lazy_gettext("Amount"),
        render_kw={"placeholder": trans.lazy_gettext("Amount")},
        validators=[
            validators.InputRequired(),
        ],
    )

    def amount_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="amount")

    def plan_id_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="plan_id")


class CompanySearchForm(Form):
    choices = [
        ("Name", trans.lazy_gettext("Name")),
        ("Email", trans.lazy_gettext("Email")),
    ]
    select = SelectField(
        trans.lazy_gettext("Search for company"),
        choices=choices,
        validators=[validators.DataRequired()],
    )
    search = StringField(
        trans.lazy_gettext("Search term"),
        validators=[
            FieldMustExist(message=trans.lazy_gettext("Required")),
        ],
    )

    def get_query_string(self) -> str:
        return self.data["search"]

    def get_category_string(self) -> str:
        return self.data["select"]


class CreateDraftForm(Form):
    prd_name = StringField(
        validators=[
            validators.InputRequired(),
            validators.Length(max=100),
        ]
    )
    description = TextAreaField(validators=[validators.InputRequired()])
    timeframe = IntegerField(
        validators=[validators.InputRequired(), validators.NumberRange(min=1, max=365)]
    )
    prd_unit = StringField(validators=[validators.InputRequired()])
    prd_amount = IntegerField(
        validators=[validators.InputRequired(), validators.NumberRange(min=1)]
    )
    costs_p = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)]
    )
    costs_r = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)]
    )
    costs_a = DecimalField(
        validators=[validators.InputRequired(), validators.NumberRange(min=0)]
    )
    productive_or_public = BooleanField(
        trans.lazy_gettext("This plan is a public service")
    )
    action = StringField()

    def product_name_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="prd_name")

    def description_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="description")

    def timeframe_field(self) -> WtFormField[int]:
        return WtFormField(form=self, field_name="timeframe")

    def unit_of_distribution_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="prd_unit")

    def amount_field(self) -> WtFormField[int]:
        return WtFormField(form=self, field_name="prd_amount")

    def means_cost_field(self) -> WtFormField[Decimal]:
        return WtFormField(form=self, field_name="costs_p")

    def resource_cost_field(self) -> WtFormField[Decimal]:
        return WtFormField(form=self, field_name="costs_r")

    def labour_cost_field(self) -> WtFormField[Decimal]:
        return WtFormField(form=self, field_name="costs_a")

    def is_public_service_field(self) -> WtFormField[bool]:
        return WtFormField(form=self, field_name="productive_or_public")


class InviteWorkerToCompanyForm(Form):
    member_id = StringField(
        validators=[
            FieldMustExist(message=trans.lazy_gettext("Required")),
        ],
        render_kw={"placeholder": trans.lazy_gettext("Member ID")},
    )

    def get_worker_id(self) -> str:
        return self.data["member_id"]


class CreateCooperationForm(Form):
    name = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Name")},
        validators=[validators.InputRequired()],
    )
    definition = TextAreaField(
        render_kw={"placeholder": trans.lazy_gettext("Definition")},
        validators=[validators.InputRequired()],
    )

    def get_name_string(self) -> str:
        return self.data["name"]

    def get_definition_string(self) -> str:
        return self.data["definition"]


class RequestCooperationForm(Form):
    plan_id = StringField()
    cooperation_id = StringField()

    def get_plan_id_string(self) -> str:
        return self.data["plan_id"]

    def get_cooperation_id_string(self) -> str:
        return self.data["cooperation_id"]


class PayMeansOfProductionForm(Form):
    plan_id = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Plan ID")},
        validators=[
            validators.InputRequired(),
        ],
    )
    amount = StringField(
        render_kw={"placeholder": trans.lazy_gettext("Amount")},
        validators=[
            validators.InputRequired(),
        ],
    )
    choices = [
        ("", ""),
        ("Fixed", trans.lazy_gettext(trans.lazy_gettext("Fixed means of production"))),
        (
            "Liquid",
            trans.lazy_gettext("Liquid means of production"),
        ),
    ]
    category = SelectField(
        trans.lazy_gettext("Type of payment"),
        choices=choices,
        validators=[validators.DataRequired()],
    )

    def amount_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="amount")

    def plan_id_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="plan_id")

    def category_field(self) -> WtFormField[str]:
        return WtFormField(form=self, field_name="category")


class AnswerCompanyWorkInviteForm(Form):
    is_accepted = BooleanField()

    def get_is_accepted_field(self) -> bool:
        return self.data["is_accepted"]
