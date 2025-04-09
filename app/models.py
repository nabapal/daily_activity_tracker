from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))  # 'team_lead' or 'member'
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    activities = db.relationship('Activity', backref='author', lazy='dynamic')
    assigned_activities = db.relationship('Activity', foreign_keys='Activity.assigned_to', backref='assignee')
    assigned_by_me = db.relationship('Activity', foreign_keys='Activity.assigner_id', backref='assigner')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    members = db.relationship('User', backref='team', lazy='dynamic')
    team_lead_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_lead = db.relationship('User', foreign_keys=[team_lead_id])

class DropdownOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))  # 'node_name', 'activity_type', 'status'
    name = db.Column(db.String(100))
    value = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(20), unique=True, nullable=False)
    details = db.Column(db.Text, nullable=False)
    node_name = db.Column(db.String(50))
    activity_type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    duration = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def calculate_duration(self):
        if self.end_date and self.activity_type == 'Completed':
            delta = self.end_date - self.start_date
            self.duration = round(delta.total_seconds() / 3600, 2)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))