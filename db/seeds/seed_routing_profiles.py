import uuid
import sys
import os

# Add backend directory to sys path so we can import our models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.authority import Authority, RoutingProfile

def seed():
    # Sync database URL
    url = os.getenv("DATABASE_URL", settings.database_url)
    if "postgresql+asyncpg://" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    elif "postgresql://" in url:
         url = url.replace("postgresql://", "postgresql+psycopg://")

    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Seeding routing profiles...")

    # Clear existing routing profiles
    session.query(RoutingProfile).delete()

    # Query authorities grouped by location (state, district) and type
    authorities = session.query(Authority).all()
    auth_map = {} # (state, district, authority_type) -> id
    for auth in authorities:
        auth_map[(auth.state, auth.district, auth.authority_type)] = auth.id

    locations = [
        ("Uttar Pradesh", "Meerut"),
        ("Punjab", "Bathinda"),
        ("Karnataka", "Chikkamagaluru")
    ]

    seed_data = []

    for state, district in locations:
        # Check if we have the seeded authorities for this location
        fire_id = auth_map.get((state, district, "FIRE_RESPONSE"))
        cpcb_id = auth_map.get((state, district, "POLLUTION_CONTROL"))
        deoc_id = auth_map.get((state, district, "DISTRICT_EMERGENCY"))
        forest_id = auth_map.get((state, district, "FOREST_RESPONSE"))
        plant_id = auth_map.get((state, district, "PLANT_EMERGENCY"))

        if not (fire_id and cpcb_id and deoc_id and forest_id and plant_id):
            print(f"Skipping {state} - {district}: missing some authorities in map.")
            continue

        # 1. Industrial Incident -> primary: Plant Emergency, secondary: Fire Services, District Emergency
        seed_data.append({
            "id": uuid.uuid4(),
            "name": f"industrial_incident_{district.lower()}",
            "state": state,
            "district": district,
            "classification": "Industrial Incident",
            "primary_authority_id": plant_id,
            "secondary_authority_ids": [fire_id, deoc_id],
            "rules": {"notify_immediate": True, "escalate_after_mins": 30}
        })

        # 2. Forest Fire -> primary: Forest Department, secondary: Fire Services, District Emergency
        seed_data.append({
            "id": uuid.uuid4(),
            "name": f"forest_fire_{district.lower()}",
            "state": state,
            "district": district,
            "classification": "Forest Fire",
            "primary_authority_id": forest_id,
            "secondary_authority_ids": [fire_id, deoc_id],
            "rules": {"notify_immediate": True, "escalate_after_mins": 60}
        })

        # 3. Agricultural Burn -> primary: Pollution Control Board (CPCB), secondary: District Emergency
        seed_data.append({
            "id": uuid.uuid4(),
            "name": f"agricultural_burn_{district.lower()}",
            "state": state,
            "district": district,
            "classification": "Agricultural Burn",
            "primary_authority_id": cpcb_id,
            "secondary_authority_ids": [deoc_id],
            "rules": {"notify_immediate": False, "suppress_during_day": True}
        })

        # 4. Persistent Flare/Kiln -> primary: Pollution Control Board (CPCB), secondary: Plant Emergency
        seed_data.append({
            "id": uuid.uuid4(),
            "name": f"persistent_flare_{district.lower()}",
            "state": state,
            "district": district,
            "classification": "Persistent Flare/Kiln",
            "primary_authority_id": cpcb_id,
            "secondary_authority_ids": [plant_id],
            "rules": {"auto_suppress_expected_hours": True}
        })

        # 5. Unknown -> primary: District Emergency
        seed_data.append({
            "id": uuid.uuid4(),
            "name": f"unknown_event_{district.lower()}",
            "state": state,
            "district": district,
            "classification": "Unknown",
            "primary_authority_id": deoc_id,
            "secondary_authority_ids": [],
            "rules": {"manual_review_required": True}
        })

    for item in seed_data:
        profile = RoutingProfile(**item)
        session.add(profile)

    session.commit()
    print(f"Successfully seeded {len(seed_data)} routing profiles!")
    session.close()

if __name__ == "__main__":
    seed()
