
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class TeamActivityForm(FlaskForm):
    assigned_to = SelectField('Assign To', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Activity')

class AddDropdownOptionForm(FlaskForm):
    dropdown_type = SelectField('Dropdown Type', choices=[
        ('status', 'Status'),
        ('activity_type', 'Activity Type'),
        ('node_name', 'Node Name')
    ], validators=[DataRequired()])
    
    option_value = StringField('Option Value', validators=[DataRequired()])
    
    submit = SubmitField('Add Option')