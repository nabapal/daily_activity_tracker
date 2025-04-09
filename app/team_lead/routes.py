from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Activity, Team, DropdownOption
from app.main.forms import DropdownOptionForm, AssignActivityForm

bp = Blueprint('team_lead', __name__, url_prefix='/team_lead')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'team_lead':
        abort(403)
    
    team_members = User.query.filter_by(team_id=current_user.team_id).all()
    activities = Activity.query.filter(
        (Activity.user_id.in_([u.id for u in team_members])) |
        (Activity.assigned_to.in_([u.id for u in team_members]))
    ).order_by(Activity.start_date.desc()).all()
    
    return render_template('team_lead/dashboard.html',
                         activities=activities,
                         team_members=team_members)

@bp.route('/dropdown_options', methods=['GET', 'POST'])
@login_required
def manage_dropdowns():
    if current_user.role != 'team_lead':
        abort(403)
        
    form = DropdownOptionForm()
    # Populate dropdown choices from DB
    form.node_name.choices = [(opt.value, opt.name) for opt in 
                             DropdownOption.query.filter_by(
                                 category='node_name',
                                 team_id=current_user.team_id
                             )]
    
    if form.validate_on_submit():
        option = DropdownOption(
            category=form.category.data,
            name=form.name.data,
            value=form.value.data,
            team_id=current_user.team_id
        )
        db.session.add(option)
        db.session.commit()
        flash('Dropdown option added!', 'success')
        return redirect(url_for('team_lead.manage_dropdowns'))
    
    options = DropdownOption.query.filter_by(team_id=current_user.team_id).all()
    return render_template('team_lead/dropdown_options.html',
                         form=form,
                         options=options)

@bp.route('/assign_activity/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def assign_activity(activity_id):
    if current_user.role != 'team_lead':
        abort(403)
        
    activity = Activity.query.get_or_404(activity_id)
    form = AssignActivityForm()
    form.users.choices = [(u.id, u.username) for u in 
                         User.query.filter(
                             User.team_id == current_user.team_id,
                             User.id != current_user.id
                         )]
    
    if form.validate_on_submit():
        for user_id in form.users.data:
            new_activity = Activity(
                activity_id=f"{activity.activity_id}-A{user_id}",
                details=activity.details,
                node_name=activity.node_name,
                activity_type=activity.activity_type,
                status=activity.status,
                start_date=activity.start_date,
                end_date=activity.end_date,
                duration=activity.duration,
                user_id=user_id,
                assigner_id=current_user.id
            )
            db.session.add(new_activity)
        db.session.commit()
        flash('Activity assigned successfully!', 'success')
        return redirect(url_for('team_lead.dashboard'))
    
    return render_template('team_lead/assign_activity.html',
                         form=form,
                         activity=activity)
@bp.route('/delete_option/<int:option_id>')
@login_required
def delete_option(option_id):
    if current_user.role != 'team_lead':
        abort(403)
    option = DropdownOption.query.get_or_404(option_id)
    if option.team_id != current_user.team_id:
        abort(403)
    db.session.delete(option)
    db.session.commit()
    flash('Option deleted', 'success')
    return redirect(url_for('team_lead.manage_dropdowns'))