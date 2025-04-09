from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.main import bp
from app.models import Activity, ActivityType, NodeName, StatusType
from app.main.forms import ActivityForm
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import time

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    activities = current_user.activities.order_by(Activity.start_date.desc()).all()
    
    # Calculate total hours, filtering out None values
    total_hours = sum(act.duration for act in activities if act.duration is not None)
    
    # Count completed activities
    completed_count = len([act for act in activities 
                         if act.activity_type == ActivityType.COMPLETED])
    
    # Count in-progress activities
    in_progress_count = len([act for act in activities 
                           if act.activity_type == ActivityType.IN_PROGRESS])
    
    return render_template('dashboard.html',
                         activities=activities,
                         total_hours=total_hours,
                         completed_count=completed_count,
                         in_progress_count=in_progress_count,
                         ActivityType=ActivityType)

@bp.route('/add_activity', methods=['GET', 'POST'])
@login_required
def add_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                activity = Activity(
                    details=form.details.data,
                    node_name=NodeName[form.node_name.data],
                    activity_type=ActivityType[form.activity_type.data],
                    status=StatusType[form.status.data],
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    user_id=current_user.id
                )
                
                db.session.add(activity)
                db.session.flush()  # Generate ID before commit
                
                if activity.activity_type == ActivityType.COMPLETED:
                    activity.calculate_duration()
                
                db.session.commit()
                flash('Activity added successfully!', 'success')
                return redirect(url_for('main.dashboard'))
                
            except IntegrityError:
                db.session.rollback()
                if attempt == max_retries - 1:
                    flash('Error creating activity. Please try again.', 'danger')
                time.sleep(0.1)
    
    return render_template('activity/add_edit.html', form=form, title='Add Activity')

@bp.route('/edit_activity/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        abort(403)
    
    form = ActivityForm(obj=activity)
    
    # Convert enum values to strings for form initialization
    form.node_name.data = activity.node_name.name
    form.activity_type.data = activity.activity_type.name
    form.status.data = activity.status.name
    
    if form.validate_on_submit():
        try:
            # Update all fields directly (no enum conversion needed)
            form.populate_obj(activity)
            
            # Manually set enum fields
            activity.node_name = NodeName[form.node_name.data]
            activity.activity_type = ActivityType[form.activity_type.data] 
            activity.status = StatusType[form.status.data]
            
            # Handle duration calculation
            if activity.activity_type == ActivityType.COMPLETED:
                activity.calculate_duration()
            
            db.session.commit()
            flash('Activity updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating activity: {str(e)}', 'danger')
    
    return render_template('activity/add_edit.html',
                         form=form,
                         title='Edit Activity',
                         activity=activity)

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

@bp.route('/reports')
@login_required
def reports():
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    activity_type = request.args.get('activity_type')
    
    # Base query
    query = Activity.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if start_date:
        query = query.filter(Activity.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Activity.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if activity_type:
        query = query.filter(Activity.name == activity_type)
    
    # Get report activities
    report_activities = query.order_by(Activity.date.desc()).all()
    
    # Get activity types for filter dropdown
    activity_types = db.session.query(Activity.name)\
        .filter_by(user_id=current_user.id)\
        .distinct()\
        .all()
    activity_types = [a[0] for a in activity_types]
    
    # Prepare data for weekly chart
    weekly_data = []
    weekly_labels = []
    
    # Get last 7 days data
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        total = db.session.query(func.sum(Activity.duration))\
            .filter_by(user_id=current_user.id)\
            .filter(func.date(Activity.date) == day.date())\
            .scalar() or 0
        weekly_data.append(float(total))
        weekly_labels.append(day.strftime('%a'))
    
    # Get activity distribution data (only if activities exist)
    activity_labels = []
    activity_data = []
    
    if report_activities:
        activity_dist = db.session.query(
                Activity.name,
                func.sum(Activity.duration).label('total_duration')
            )\
            .filter_by(user_id=current_user.id)\
            .group_by(Activity.name)\
            .all()
        
        activity_labels = [a[0] for a in activity_dist]
        activity_data = [float(a[1]) for a in activity_dist]
    
    return render_template('activity/reports.html',
                         report_activities=report_activities,
                         activity_types=activity_types,
                         weekly_labels=weekly_labels,
                         weekly_data=weekly_data,
                         activity_labels=activity_labels,
                         activity_data=activity_data)