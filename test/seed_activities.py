import sys
from pathlib import Path
from datetime import datetime, timedelta
from random import choice, randint

# Configure paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app import create_app, db
from app.models import User, DropdownOption, Activity
from app.config.constants import TEAMS

# Status configuration (using display texts as values)
STATUS_OPTIONS = [
    ('Yet To Start', 'Yet To Start'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled')
]

def seed_activities():
    app = create_app()
    with app.app_context():
        try:
            statuses = [status[0] for status in STATUS_OPTIONS]
            
            # Get all seeded data
            all_nodes = {team: [] for team in TEAMS}
            all_activity_types = {team: [] for team in TEAMS}
            
            for option in DropdownOption.query.all():
                if option.category == 'node_name':
                    all_nodes[option.team].append(option)
                elif option.category == 'activity_type':
                    all_activity_types[option.team].append(option)
            
            # Create activities (10 per user)
            for team in TEAMS:
                team_users = User.query.filter_by(team=team).all()
                nodes = all_nodes[team]
                activity_types = all_activity_types[team]
                
                for user in team_users:
                    for i in range(1, 11):  # 10 activities per user
                        # Ensure coverage of all node/activity types
                        if i <= 4:
                            node = nodes[i-1]
                            activity_type = activity_types[i-1]
                        else:
                            node = choice(nodes)
                            activity_type = choice(activity_types)
                        
                        start_date = datetime.utcnow() - timedelta(days=randint(0, 30))
                        end_date = start_date + timedelta(hours=randint(1, 8)) if choice([True, False]) else None
                        
                        activity = Activity(
                            activity_id=f"ACT-{team[:3]}-{user.id}-{i:03d}",
                            details=f"Activity #{i} for {user.username} ({team})",
                            node_name=node.value,
                            activity_type=activity_type.value,
                            status=choice(statuses),  # Corrected status values
                            start_date=start_date,
                            end_date=end_date,
                            user_id=user.id,
                            assigned_to=user.id
                        )
                        if end_date:
                            activity.calculate_duration()
                        db.session.add(activity)
            
            db.session.commit()
            print(f"✅ Created {len(TEAMS)*50} activities with correct status values")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    seed_activities()