from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Activity, DropdownOption, Team
from app.main.forms import LoginForm, RegistrationForm, ActivityForm, EditProfileForm, ReportFilterForm
from app.main import bp

@bp.route('/')
def index():
    """Landing page for non-authenticated users"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for authenticated users"""
    page = request.args.get('page', 1, type=int)
    activities = current_user.activities.order_by(
        Activity.start_time.desc()).paginate(
            page=page, per_page=10, error_out=False)
    
    # Get display names for activity types and statuses
    for activity in activities.items:
        activity.type_display = DropdownOption.get_display_text('activity_type', activity.activity_type)
        activity.status_display = DropdownOption.get_display_text('status', activity.status)
    
    return render_template('dashboard.html', 
                         title='Dashboard',
                         activities=activities)

@bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    """Generate and display activity reports"""
    form = ReportFilterForm()
    
    # Set dynamic choices for filters
    form.activity_type.choices = [('', 'All')] + [
        (opt.value, opt.display_text) 
        for opt in DropdownOption.get_options('activity_type')
    ]
    form.status.choices = [('', 'All')] + [
        (opt.value, opt.display_text) 
        for opt in DropdownOption.get_options('status')
    ]
    form.team.choices = [('', 'All')] + [
        (team.id, team.name) 
        for team in Team.query.all()
    ]

    activities = current_user.activities.order_by(Activity.start_time.desc())
    
    if form.validate_on_submit():
        # Apply filters
        if form.start_date.data:
            activities = activities.filter(Activity.start_time >= form.start_date.data)
        if form.end_date.data:
            activities = activities.filter(Activity.start_time <= form.end_date.data)
        if form.activity_type.data:
            activities = activities.filter(Activity.activity_type == form.activity_type.data)
        if form.status.data:
            activities = activities.filter(Activity.status == form.status.data)
        if form.team.data:
            activities = activities.filter(Activity.team_id == form.team.data)

    activities = activities.all()
    
    # Add display texts
    for activity in activities:
        activity.type_display = DropdownOption.get_display_text('activity_type', activity.activity_type)
        activity.status_display = DropdownOption.get_display_text('status', activity.status)
    
    return render_template('reports.html',
                         title='Reports',
                         form=form,
                         activities=activities)
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/add_activity', methods=['GET', 'POST'])
@login_required
def add_activity():
    form = ActivityForm()
    
    # Set dynamic choices
    form.activity_type.choices = [
        (opt.value, opt.display_text) 
        for opt in DropdownOption.get_options('activity_type')
    ]
    form.status.choices = [
        (opt.value, opt.display_text) 
        for opt in DropdownOption.get_options('status')
    ]
    form.team.choices = [
        (team.id, team.name) 
        for team in Team.query.all()
    ]
    
    if form.validate_on_submit():
        activity = Activity(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            activity_type=form.activity_type.data,
            status=form.status.data,
            team_id=form.team.data,
            user_id=current_user.id
        )
        db.session.add(activity)
        db.session.commit()
        flash('Your activity has been added!')
        return redirect(url_for('main.dashboard'))
    return render_template('add_activity.html', title='Add Activity', form=form)

@bp.route('/edit_activity/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        abort(403)
        
    form = ActivityForm()
    
    # Set dynamic choices
    form.activity_type.choices = [
        (opt.value, opt.display_text) 
        for opt in DropdownOption.get_options('activity_type')
    ]
    form.status.choices = [
        (opt.value, opt.display_text) 
        for opt in DropdownOption.get_options('status')
    ]
    form.team.choices = [
        (team.id, team.name) 
        for team in Team.query.all()
    ]
    
    if form.validate_on_submit():
        activity.title = form.title.data
        activity.description = form.description.data
        activity.start_time = form.start_time.data
        activity.end_time = form.end_time.data
        activity.activity_type = form.activity_type.data
        activity.status = form.status.data
        activity.team_id = form.team.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.dashboard'))
    
    # Pre-populate form for GET request
    if request.method == 'GET':
        form.title.data = activity.title
        form.description.data = activity.description
        form.start_time.data = activity.start_time
        form.end_time.data = activity.end_time
        form.activity_type.data = activity.activity_type
        form.status.data = activity.status
        form.team.data = activity.team_id
    
    return render_template('edit_activity.html', title='Edit Activity', form=form)

@bp.route('/delete_activity/<int:id>', methods=['POST'])
@login_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.user_id != current_user.id:
        abort(403)
    db.session.delete(activity)
    db.session.commit()
    flash('Your activity has been deleted.')
    return redirect(url_for('main.dashboard'))

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    activities = user.activities.order_by(Activity.start_time.desc()).all()
    
    # Add display texts
    for activity in activities:
        activity.type_display = DropdownOption.get_display_text('activity_type', activity.activity_type)
        activity.status_display = DropdownOption.get_display_text('status', activity.status)
    
    return render_template('user.html', user=user, activities=activities)