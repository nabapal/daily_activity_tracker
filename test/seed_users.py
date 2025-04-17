import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app, db
from app.models import User
from app.config.constants import TEAMS

def generate_team_emails(team_key, username):
    return f"{username}@{team_key.lower()}.example.com"

def seed_users():
    app = create_app()
    with app.app_context():
        try:
            for team_key in TEAMS.keys():
                # Team Lead
                lead = User(
                    username=f"lead_{team_key}",
                    email=generate_team_emails(team_key, f"lead_{team_key}"),
                    role='team_lead',
                    team=team_key
                )
                lead.set_password("Lead@123")
                db.session.add(lead)

                # Members
                for i in range(1, 5):
                    member = User(
                        username=f"user{i}_{team_key}",
                        email=generate_team_emails(team_key, f"user{i}"),
                        role='member',
                        team=team_key
                    )
                    member.set_password(f"Member{i}@123")
                    db.session.add(member)

            db.session.commit()
            print(f"✅ Created {len(TEAMS)*5} users for {len(TEAMS)} teams")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    seed_users()