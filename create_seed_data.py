# create_seed_data.py
from app import create_app, db
from app.models import User, DropdownOption
from config import Config

app = create_app()
app.app_context().push()

# Create admin user
if not User.query.first():
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin',
        team='development'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()

# Seed dropdown options
for category, options in Config.DEFAULT_DROPDOWN_OPTIONS.items():
    for value, display in options:
        if not DropdownOption.query.filter_by(
            category=category,
            value=value,
            team=Config.DEFAULT_TEAM
        ).first():
            option = DropdownOption(
                category=category,
                display_text=display,
                value=value,
                team=Config.DEFAULT_TEAM,
                created_by=1  # admin user ID
            )
            db.session.add(option)
db.session.commit()
