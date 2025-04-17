# app/config/constants.py

# Teams Configuration
TEAMS = {
    'IPSE': 'IPSE Team',
    'TELCO': 'Telco Team',
    'IPMPLS': 'IPMPLS Team',
    'OPtical': 'Optical Team',
    'Microwave': 'Microwave Team'
}

# Roles Configuration
ROLES = {
    'member': 'Regular Member',
    'team_lead': 'Team Lead', 
    'admin': 'Administrator'
}

# Dropdown Categories
DROPDOWN_CATEGORIES = {
    'node_name': 'Node Name',
    'activity_type': 'Activity Type',
    'status': 'Status'
}

# Default Dropdown Options
DEFAULT_DROPDOWN_OPTIONS = {
    'status': [
        ('yet_to_start', 'Yet To Start'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold')
    ],
    'activity_type': [
        ('meeting', 'Meeting'),
        ('coding', 'Coding'),
        ('testing', 'Testing')
    ]
}

# System Defaults
DEFAULT_TEAM = 'development'
DEFAULT_ROLE = 'member'