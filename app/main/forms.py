from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
                    TextAreaField, SelectField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('member', 'Team Member'), ('team_lead', 'Team Lead')])
    team_name = StringField('Team Name (new or existing)')
    submit = SubmitField('Register')

class DropdownOptionForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('node_name', 'Node Name'),
        ('activity_type', 'Activity Type'),
        ('status', 'Status')
    ], validators=[DataRequired()])
    name = StringField('Display Name', validators=[DataRequired()])
    value = StringField('System Value', validators=[DataRequired()])
    submit = SubmitField('Add Option')

class ActivityForm(FlaskForm):
    details = TextAreaField('Activity Details', validators=[DataRequired()])
    node_name = SelectField('Node Name', validators=[DataRequired()])
    activity_type = SelectField('Activity Type', validators=[DataRequired()])
    status = SelectField('Status', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    submit = SubmitField('Save Activity')

class AssignActivityForm(FlaskForm):
    users = SelectMultipleField('Assign to Users', coerce=int)
    submit = SubmitField('Assign')