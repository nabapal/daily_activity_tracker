import sys
from pathlib import Path
from datetime import datetime, timedelta
from random import choice

# Configure paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from app import create_app, db
from app.models import User, DropdownOption, Activity
from app.config.constants import TEAMS
print("Test")
# Configuration
STATUS_OPTIONS = [
    ('yet_to_start', 'Yet To Start'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled')
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

def seed_all():
    app = create_app()
    with app.app_context():
        try:
            # Clear existing test data
            db.session.query(DropdownOption).delete()
            
            # 1. Seed Status Options (same for all teams)
            for status in STATUS_OPTIONS:
                for team in TEAMS:
                    if not DropdownOption.query.filter_by(
                        category='status',
                        value=status[0],
                        team=team
                    ).first():
                        db.session.add(DropdownOption(
                            category='status',
                            display_text=status[1],
                            value=status[0],
                            team=team,
                            created_by=User.query.filter_by(
                                username=f'lead_{team}'
                            ).first().id
                        ))
            
            # 2. Seed Nodes for each team
            for team, prefixes in NODE_PREFIXES.items():
                for i, prefix in enumerate(prefixes, 1):
                    db.session.add(DropdownOption(
                        category='node_name',
                        display_text=f"{prefix}-{team[:3]}-{i:02d}",
                        value=f"{prefix}-{team[:3]}-{i:02d}",
                        team=team,
                        created_by=User.query.filter_by(
                            username=f'lead_{team}'
                        ).first().id
                    ))
            
            # 3. Seed Activity Types for each team
            for team, types in ACTIVITY_TYPES.items():
                for activity_type in types:
                    db.session.add(DropdownOption(
                        category='activity_type',
                        display_text=activity_type,
                        value=activity_type.lower().replace(' ', '_'),
                        team=team,
                        created_by=User.query.filter_by(
                            username=f'lead_{team}'
                        ).first().id
                    ))
            
            db.session.commit()
            print("✅ Successfully seeded:")
            print(f"- {len(TEAMS)*len(STATUS_OPTIONS)} status options")
            print(f"- {sum(len(v) for v in NODE_PREFIXES.values())} nodes")
            print(f"- {sum(len(v) for v in ACTIVITY_TYPES.values())} activity types")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding data: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    seed_all()