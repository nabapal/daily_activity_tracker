from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin', 'team_lead', 'member'
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    # Relationships
    activities = db.relationship('Activity', backref='author', lazy='dynamic',
                               foreign_keys='Activity.user_id')
    assigned_activities = db.relationship('Activity', backref='assignee',
                                        foreign_keys='Activity.assigned_to',
                                        lazy='dynamic')
    assigned_by_me = db.relationship('Activity', backref='assigner',
                                    foreign_keys='Activity.assigner_id',
                                    lazy='dynamic')
    led_team = db.relationship('Team', backref='team_lead',
                              foreign_keys='Team.team_lead_id',
                              uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_team_lead(self):
        return self.role == 'team_lead'

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    team_lead_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    members = db.relationship('User', backref='team', lazy='dynamic')
    dropdown_options = db.relationship('DropdownOption', backref='team', lazy='dynamic')

class DropdownOption(db.Model):
    __tablename__ = 'dropdown_options'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # 'node_name', 'activity_type', 'status'
    display_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    __table_args__ = (
        db.UniqueConstraint('category', 'value', 'team_id', name='unique_option_per_team'),
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
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def calculate_duration(self):
        if self.end_date and self.status == 'completed':
            delta = self.end_date - self.start_date
            self.duration = round(delta.total_seconds() / 3600, 2)
            return self.duration
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))