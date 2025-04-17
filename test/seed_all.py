import sys
from pathlib import Path
from datetime import datetime, timedelta
from random import choice, randint
from uuid import uuid4
from collections import defaultdict

# Configure paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app import create_app, db
from app.models import User, DropdownOption, Activity
from app.config.constants import TEAMS

# Updated Configuration
STATUS_OPTIONS = [
    ('yet_to_start', 'Yet To Start'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('on_hold', 'On Hold')  # Changed from 'cancelled'
]

NODE_PREFIXES = {
    'IPSE': ['RNC', 'BSC', 'MGW', 'HLR'],
    'TELCO': ['BTS', 'BSC', 'MSC', 'GGSN'],
    'IPMPLS': ['PE', 'CE', 'P', 'ASBR'],
    'OPtical': ['OLT', 'ONT', 'ODN', 'OSU'],
    'Microwave': ['IDU', 'ODU', 'ANT', 'RF']
}

ACTIVITY_TYPES = {
    'IPSE': ['Maintenance', 'Upgrade', 'Troubleshooting', 'Configuration'],
    'TELCO': ['Installation', 'Commissioning', 'Optimization', 'Audit'],
    'IPMPLS': ['Provisioning', 'Migration', 'QoS Setup', 'Security Patch'],
    'OPtical': ['Fiber Test', 'Splicing', 'OTDR Test', 'Power Adjustment'],
    'Microwave': ['Alignment', 'Path Survey', 'Throughput Test', 'Firmware Update']
}

def generate_email(username: str, team: str) -> str:
    return f"{username}@{team.lower()}.test.com"

def generate_activity_id(team: str) -> str:
    return f"ACT-{team[:3]}-{str(uuid4())[:8]}"

def wipe_all_data():
    """Clears all test data using direct SQL"""
    # Disable foreign key checks temporarily (SQLite specific)
    db.session.execute("PRAGMA foreign_keys=OFF")
    
    # Clear tables in safe order
    db.session.execute("DELETE FROM activities")
    db.session.execute("DELETE FROM dropdown_options")
    
    # Delete only test users (leads and numbered users)
    db.session.execute("""
        DELETE FROM users 
        WHERE username LIKE 'lead\\_%' ESCAPE '\\' 
           OR username LIKE 'usr%\\_%' ESCAPE '\\'
    """)
    
    # Re-enable foreign keys
    db.session.execute("PRAGMA foreign_keys=ON")
    db.session.commit()

def seed_all():
    app = create_app()
    with app.app_context():
        try:
            print("♻️  Clearing all existing test data...")
            wipe_all_data()

            # 1. SEED USERS
            print("👥 Creating users...")
            for team_key in TEAMS:
                # Team Lead
                lead = User(
                    username=f"lead_{team_key}",
                    email=generate_email(f"lead_{team_key}", team_key),
                    role='team_lead',
                    team=team_key
                )
                lead.set_password("Lead@123")
                db.session.add(lead)

                # Members (4 per team)
                for i in range(1, 5):
                    member = User(
                        username=f"usr{i}_{team_key}",
                        email=generate_email(f"usr{i}", team_key),
                        role='member',
                        team=team_key
                    )
                    member.set_password(f"Member{i}@123")
                    db.session.add(member)
            
            db.session.commit()

            # 2. SEED DROPDOWNS
            print("📋 Creating dropdown options...")
            for team_key in TEAMS:
                lead_id = User.query.filter_by(username=f"lead_{team_key}").first().id
                
                # Status Options (with on_hold instead of cancelled)
                for status in STATUS_OPTIONS:
                    db.session.add(DropdownOption(
                        category='status',
                        display_text=status[1],
                        value=status[0],
                        team=team_key,
                        created_by=lead_id
                    ))

                # Nodes
                for i, prefix in enumerate(NODE_PREFIXES[team_key], 1):
                    db.session.add(DropdownOption(
                        category='node_name',
                        display_text=f"{prefix}-{team_key[:3]}-{i:02d}",
                        value=f"{prefix}-{team_key[:3]}-{i:02d}",
                        team=team_key,
                        created_by=lead_id
                    ))

                # Activity Types
                for activity_type in ACTIVITY_TYPES[team_key]:
                    db.session.add(DropdownOption(
                        category='activity_type',
                        display_text=activity_type,
                        value=activity_type.lower().replace(' ', '_'),
                        team=team_key,
                        created_by=lead_id
                    ))
            
            db.session.commit()

            # 3. SEED ACTIVITIES (with updated status options)
            print("✅ Creating activities...")
            status_values = [status[1] for status in STATUS_OPTIONS]
            
            for team_key in TEAMS:
                users = User.query.filter_by(team=team_key).all()
                nodes = DropdownOption.query.filter_by(
                    category='node_name', 
                    team=team_key
                ).all()
                activity_types = DropdownOption.query.filter_by(
                    category='activity_type',
                    team=team_key
                ).all()

                for user in users:
                    for i in range(10):
                        if i < 4:
                            node = nodes[i % len(nodes)]
                            activity_type = activity_types[i % len(activity_types)]
                        else:
                            node = choice(nodes)
                            activity_type = choice(activity_types)

                        start_date = datetime.utcnow() - timedelta(days=randint(0, 30))
                        end_date = start_date + timedelta(hours=randint(1, 8)) if choice([True, False]) else None

                        activity = Activity(
                            activity_id=generate_activity_id(team_key),
                            details=f"{activity_type.display_text} at {node.display_text}",
                            node_name=node.value,
                            activity_type=activity_type.value,
                            status=choice(status_values),  # Only uses updated status options
                            start_date=start_date,
                            end_date=end_date,
                            user_id=user.id,
                            assigned_to=user.id
                        )
                        if end_date:
                            activity.calculate_duration()
                        db.session.add(activity)
            
            db.session.commit()
            print("🌱 Seeding complete with updated status options!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    seed_all()