from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from app import db
from app.models import User, Activity, DropdownOption
from app.team_lead import bp
from app.team_lead.forms import TeamActivityForm
from config import Config

@bp.route('/team_dashboard')
@login_required
def team_dashboard():
    if not current_user.is_team_lead:
        abort(403)
    
    # Get team members
    team_members = User.query.filter_by(team=current_user.team).all()
    
    # Get team activities
    activities = Activity.query.join(
        User, Activity.user_id == User.id
    ).filter(
        User.team == current_user.team
    ).order_by(Activity.start_date.desc()).all()
    
    return render_template('team_lead/team_dashboard.html',
                         team_members=team_members,
                         activities=activities,
                         current_team=current_user.team)

@bp.route('/assign_activity/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def assign_activity(activity_id):
    if not current_user.is_team_lead:
        abort(403)
    
    activity = Activity.query.get_or_404(activity_id)
    form = TeamActivityForm()
    
    # Populate members from current team only
    form.assigned_to.choices = [
        (member.id, member.username) 
        for member in User.query.filter_by(team=current_user.team).all()
    ]
    
    if form.validate_on_submit():
        activity.assigned_to = form.assigned_to.data
        activity.assigner_id = current_user.id
        activity.status = 'assigned'
        db.session.commit()
        flash('Activity has been assigned!', 'success')
        return redirect(url_for('team_lead.team_dashboard'))
    
    return render_template('team_lead/assign_activity.html',
                         form=form,
                         activity=activity)

@bp.route('/team_reports')
@login_required
def team_reports():
    if not current_user.is_team_lead:
        abort(403)
    
    # Get reports from team members
    reports = Report.query.join(
        User, Report.user_id == User.id
    ).filter(
        User.team == current_user.team
    ).order_by(Report.created_at.desc()).all()
    
    return render_template('team_lead/team_reports.html',
                         reports=reports)

@bp.route('/manage_team_dropdowns', methods=['GET', 'POST'])
@login_required
def manage_team_dropdowns():
    if not current_user.is_team_lead:
        abort(403)
    
    dropdown_options = DropdownOption.query.filter_by(
        team=current_user.team
    ).order_by(DropdownOption.category).all()
    
    return render_template('team_lead/manage_dropdowns.html',
                         dropdown_options=dropdown_options,
                         categories=Config.DROPDOWN_CATEGORIES)

@bp.route('/add_dropdown_option', methods=['GET', 'POST'])
@login_required
def add_dropdown_option():
    if not current_user.is_team_lead:
        abort(403)

    if request.method == 'POST':
        category = request.form.get('category')
        display_text = request.form.get('display_text')
        value = request.form.get('value')
        
        if not all([category, display_text, value]):
            flash('All fields are required', 'danger')
            return redirect(url_for('team_lead.add_dropdown_option'))

        # Check for duplicates
        existing = DropdownOption.query.filter_by(
            category=category,
            value=value,
            team=current_user.team
        ).first()

        if existing:
            flash('This option already exists', 'danger')
            return redirect(url_for('team_lead.add_dropdown_option'))

        option = DropdownOption(
            category=category,
            display_text=display_text,
            value=value,
            team=current_user.team,
            created_by=current_user.id
        )
        db.session.add(option)
        db.session.commit()
        flash('Dropdown option added successfully!', 'success')
        return redirect(url_for('team_lead.manage_team_dropdowns'))

    # GET request – render the form
    return render_template('team_lead/add_dropdown_option.html')


@bp.route('/delete_dropdown_option/<int:id>', methods=['POST'])
@login_required
def delete_dropdown_option(id):
    if not current_user.is_team_lead:
        abort(403)
    
    option = DropdownOption.query.get_or_404(id)
    if option.team != current_user.team:
        abort(403)
    
    db.session.delete(option)
    db.session.commit()
    flash('Dropdown option deleted successfully!', 'success')
    return redirect(url_for('team_lead.manage_team_dropdowns'))