from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from ..models import Priority, Severity, IssueType


class AddProjectForm(FlaskForm):
    code = StringField(
        description="Project ticker", validators=[DataRequired(), Length(1, 8)]
    )
    client = StringField(validators=[DataRequired()])
    title = StringField(
        description="Summary of the project", validators=[DataRequired()]
    )
    body = TextAreaField(
        description="A more detailed description", validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class AddIssueForm(FlaskForm):
    type_code = SelectField(label="Type")
    priority = SelectField()
    severity = SelectField()
    title = StringField(description="Summary of the issue", validators=[DataRequired()])
    body = TextAreaField(
        description="A more detailed description", validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class EditIssueForm(FlaskForm):
    type_code = SelectField(label="Type")
    priority = SelectField()
    severity = SelectField()
    title = StringField(description="Summary of the issue", validators=[DataRequired()])
    body = TextAreaField(
        description="A more detailed description", validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class EditProjectForm(FlaskForm):
    code = StringField(
        description="Project ticker", validators=[DataRequired(), Length(1, 8)]
    )
    client = StringField(validators=[DataRequired()])
    title = StringField(
        description="Summary of the project", validators=[DataRequired()]
    )
    body = TextAreaField(
        description="A more detailed description", validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


class AddCommentForm(FlaskForm):
    body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField("Submit")
