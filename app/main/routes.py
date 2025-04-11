from flask import render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_required
from datetime import datetime
from app import db
from app.models import User, Activity, DropdownOption, Report
from app.main import bp
from app.main.forms import (LoginForm, RegistrationForm, ActivityForm, 
                           ReportForm, DropdownOptionForm, ProfileForm)
from config import Config

# Helper functions
def get_team_options(category, team):
    return DropdownOption.query.filter_by(category=category, team=team).all()

def get_team_members(team):
    return User.query.filter_by(team=team).all()

# Routes
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    activities = Activity.query.filter(
        (Activity.user_id == current_user.id) |
        (Activity.assigned_to == current_user.id)
    ).order_by(Activity.start_date.desc()).all()
    
    return render_template('dashboard.html',
                         activities=activities,
                         node_names=get_team_options('node_name', current_user.team),
                         activity_types=get_team_options('activity_type', current_user.team),
                         statuses=get_team_options('status', current_user.team))

@bp.route('/add_activity', methods=['GET', 'POST'])
@login_required
def add_activity():
    form = ActivityForm()
    form.node_name.choices = [(o.value, o.display_text) for o in get_team_options('node_name', current_user.team)]
    form.activity_type.choices = [(o.value, o.display_text) for o in get_team_options('activity_type', current_user.team)]
    form.status.choices = [(o.value, o.display_text) for o in get_team_options('status', current_user.team)]
    form.assigned_to.choices = [(u.id, u.username) for u in get_team_members(current_user.team)]

    if form.validate_on_submit():
        activity = Activity(
            activity_id=f"ACT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            details=form.details.data,
            node_name=form.node_name.data,
            activity_type=form.activity_type.data,
            status=form.status.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id,
            assigned_to=form.assigned_to.data,
            assigner_id=current_user.id
        )
        db.session.add(activity)
        db.session.commit()
        flash('Activity created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('activity/add_edit.html', form=form)

@bp.route('/edit_activity/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        abort(403)
    
    form = ActivityForm(obj=activity)
    form.node_name.choices = [(o.value, o.display_text) for o in get_team_options('node_name', current_user.team)]
    form.activity_type.choices = [(o.value, o.display_text) for o in get_team_options('activity_type', current_user.team)]
    form.status.choices = [(o.value, o.display_text) for o in get_team_options('status', current_user.team)]
    form.assigned_to.choices = [(u.id, u.username) for u in get_team_members(current_user.team)]

    if form.validate_on_submit():
        form.populate_obj(activity)
        activity.calculate_duration()
        db.session.commit()
        flash('Activity updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('activity/add_edit.html', form=form, activity=activity)

@bp.route('/delete_activity/<int:id>', methods=['POST'])
@login_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        abort(403)
    db.session.delete(activity)
    db.session.commit()
    flash('Activity deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportForm()
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    
    if form.validate_on_submit():
        report = Report(
            title=form.title.data,
            content=form.content.data,
            report_type=form.report_type.data,
            user_id=current_user.id
        )
        db.session.add(report)
        db.session.commit()
        flash('Report generated successfully!', 'success')
        return redirect(url_for('main.reports'))
    
    return render_template('reports.html', form=form, reports=reports)

@bp.route('/team_activities')
@login_required
def team_activities():
    if not current_user.is_team_lead:
        abort(403)
    
    activities = Activity.query.join(User).filter(
        User.team == current_user.team
    ).order_by(Activity.start_date.desc()).all()
    
    return render_template(' team_activities.html',
                         activities=activities,
                         team_members=get_team_members(current_user.team))

@bp.route('/manage_dropdowns', methods=['GET', 'POST'])
@login_required
def manage_dropdowns():
    if not current_user.is_team_lead:
        abort(403)
    
    form = DropdownOptionForm()
    options = DropdownOption.query.filter_by(team=current_user.team).order_by(DropdownOption.category).all()
    
    if form.validate_on_submit():
        option = DropdownOption(
            category=form.category.data,
            display_text=form.display_text.data,
            value=form.value.data,
            team=current_user.team,
            created_by=current_user.id
        )
        db.session.add(option)
        db.session.commit()
        flash('Dropdown option added!', 'success')
        return redirect(url_for('main.manage_dropdowns'))
    
    return render_template('manage_dropdowns.html',
                         form=form,
                         options=options)

@bp.route('/delete_dropdown/<int:id>', methods=['POST'])
@login_required
def delete_dropdown(id):
    option = DropdownOption.query.get_or_404(id)
    if option.created_by != current_user.id:
        abort(403)
    db.session.delete(option)
    db.session.commit()
    flash('Dropdown option deleted!', 'success')
    return redirect(url_for('main.manage_dropdowns'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', form=form)
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))