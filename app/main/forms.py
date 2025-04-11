from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, TextAreaField, 
                    SelectField, SubmitField, DateTimeField, DateField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask import current_app

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[], validators=[DataRequired()])
    team = SelectField('Team', choices=[], validators=[DataRequired()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.role.choices = current_app.config['AVAILABLE_ROLES']
        self.team.choices = current_app.config['AVAILABLE_TEAMS']

class ActivityForm(FlaskForm):
    details = TextAreaField('Details', validators=[DataRequired()], render_kw={"rows": 5})
    node_name = SelectField('Node Name', coerce=str, validators=[DataRequired()])
    activity_type = SelectField('Activity Type', coerce=str, validators=[DataRequired()])
    status = SelectField('Status', coerce=str, validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    assigned_to = SelectField('Assign To', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Activity')

class ReportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    report_type = SelectField('Report Type', choices=[
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report')
    ], validators=[DataRequired()])
    submit = SubmitField('Generate Report')

class DropdownOptionForm(FlaskForm):
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    display_text = StringField('Display Text', validators=[DataRequired(), Length(max=100)])
    value = StringField('System Value', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Option')

    def __init__(self, *args, **kwargs):
        super(DropdownOptionForm, self).__init__(*args, **kwargs)
        self.category.choices = [(k, v) for k, v in current_app.config['DROPDOWN_CATEGORIES'].items()]

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')