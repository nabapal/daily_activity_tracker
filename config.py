# config.py
import os
from dotenv import load_dotenv
from app.config.constants import (TEAMS, ROLES, DROPDOWN_CATEGORIES,
                                DEFAULT_DROPDOWN_OPTIONS,
                                DEFAULT_TEAM, DEFAULT_ROLE)

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # App Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Teams and Roles
    AVAILABLE_TEAMS = [(k, v) for k, v in TEAMS.items()]
    AVAILABLE_ROLES = [(k, v) for k, v in ROLES.items()]
    DEFAULT_TEAM = DEFAULT_TEAM
    DEFAULT_ROLE = DEFAULT_ROLE
    
    # Dropdown Configuration
    DROPDOWN_CATEGORIES = DROPDOWN_CATEGORIES
    DEFAULT_DROPDOWN_OPTIONS = DEFAULT_DROPDOWN_OPTIONS
    
    # Pagination
    ACTIVITIES_PER_PAGE = 10
    USERS_PER_PAGE = 20