from flask import Blueprint

bp = Blueprint('team_lead', __name__)

from app.team_lead import routes  # This imports the routes after bp is defined