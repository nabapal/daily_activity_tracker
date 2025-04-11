from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    team = db.Column(db.String(20), nullable=False, default='development')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('Activity', backref='author', lazy='dynamic',
                               foreign_keys='Activity.user_id')
    assigned_activities = db.relationship('Activity', backref='assignee',
                                        foreign_keys='Activity.assigned_to',
                                        lazy='dynamic')
    assigned_by_me = db.relationship('Activity', backref='assigner',
                                    foreign_keys='Activity.assigner_id',
                                    lazy='dynamic')
    dropdown_options = db.relationship('DropdownOption', backref='creator', lazy='dynamic')
    reports = db.relationship('Report', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_team_lead(self):
        return self.role == 'team_lead'

    @property
    def is_admin(self):
        return self.role == 'admin'

class DropdownOption(db.Model):
    __tablename__ = 'dropdown_options'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    display_text = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(20), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('category', 'value', 'team', name='unique_option_per_team'),
    )

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(20), unique=True, nullable=False)
    details = db.Column(db.Text, nullable=False)
    node_name = db.Column(db.String(50))
    activity_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='pending')
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    duration = db.Column(db.Float)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_duration(self):
        if self.end_date and self.status == 'completed':
            delta = self.end_date - self.start_date
            self.duration = round(delta.total_seconds() / 3600, 2)
            return self.duration
        return None

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))