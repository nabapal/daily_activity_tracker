from flask_wtf import FlaskForm
from wtforms import (BooleanField, SelectMultipleField, StringField, PasswordField, TextAreaField, 
                    SelectField, SubmitField, DateTimeField, DateField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ActivityForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=2000)])
    start_time = DateTimeField('Start Time', format='%Y-%m-%d %H:%M', validators=[Optional()])
    end_time = DateTimeField('End Time', format='%Y-%m-%d %H:%M', validators=[Optional()])
    activity_type = SelectField('Type', coerce=str, validators=[DataRequired()])
    status = SelectField('Status', coerce=str, validators=[Optional()])
    team = SelectField('Team', coerce=int, validators=[Optional()])
    submit = SubmitField('Save')

class ReportFilterForm(FlaskForm):
    start_date = DateField('From Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('To Date', format='%Y-%m-%d', validators=[Optional()])
    activity_type = SelectField('Activity Type', coerce=str, validators=[Optional()])
    status = SelectField('Status', coerce=str, validators=[Optional()])
    team = SelectField('Team', coerce=int, validators=[Optional()])
    submit = SubmitField('Filter')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class DropdownOptionForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('node_name', 'Node Name'),
        ('activity_type', 'Activity Type'),
        ('status', 'Status')
    ], validators=[DataRequired()])
    name = StringField('Display Name', validators=[DataRequired()])
    value = StringField('System Value', validators=[DataRequired()])
    submit = SubmitField('Add Option')

class AssignActivityForm(FlaskForm):
    users = SelectMultipleField('Assign to Users', coerce=int)
    submit = SubmitField('Assign')