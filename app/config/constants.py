# app/config/constants.py

# Teams Configuration
TEAMS = {
    'development': 'Development Team',
    'marketing': 'Marketing Team',
    'sales': 'Sales Team',
    'operations': 'Operations Team'
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
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
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