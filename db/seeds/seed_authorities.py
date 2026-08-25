import uuid
import sys
import os
from datetime import date

# Add backend directory to sys path so we can import our models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.authority import Authority

def seed():
    # Sync database URL for seeds
    url = os.getenv("DATABASE_URL", settings.database_url)
    if "postgresql+asyncpg://" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    elif "postgresql://" in url:
         url = url.replace("postgresql://", "postgresql+psycopg://")
         
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Seeding authorities...")

    # Clear existing authorities
    session.query(Authority).delete()

    seed_data = [
        # --- Uttar Pradesh ---
        {
            "id": uuid.uuid4(),
            "state": "Uttar Pradesh",
            "district": "Meerut",
            "authority_type": "FIRE_RESPONSE",
            "department": "Uttar Pradesh Fire Services",
            "role": "District Fire Officer Meerut",
            "official_email": "dfo.meerut@upfire.gov.in",
            "official_phone": "+911211010101",
            "portal_url": "https://fire.up.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 1),
            "source_url": "https://up.gov.in/en/page/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Uttar Pradesh",
            "district": "Meerut",
            "authority_type": "POLLUTION_CONTROL",
            "department": "Uttar Pradesh Pollution Control Board (UPPCB)",
            "role": "Regional Officer UPPCB Meerut",
            "official_email": "ro.meerut@uppcb.gov.in",
            "official_phone": "+911211020202",
            "portal_url": "https://uppcb.com",
            "active": True,
            "verified_on": date(2026, 8, 1),
            "source_url": "https://uppcb.com/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Uttar Pradesh",
            "district": "Meerut",
            "authority_type": "DISTRICT_EMERGENCY",
            "department": "District Emergency Operations Centre (DEOC) Meerut",
            "role": "District Magistrate / DEOC In-charge",
            "official_email": "dm.meerut@up.gov.in",
            "official_phone": "+911211030303",
            "portal_url": "https://meerut.nic.in",
            "active": True,
            "verified_on": date(2026, 8, 1),
            "source_url": "https://meerut.nic.in/directory"
        },
        {
            "id": uuid.uuid4(),
            "state": "Uttar Pradesh",
            "district": "Meerut",
            "authority_type": "FOREST_RESPONSE",
            "department": "Uttar Pradesh Forest Department",
            "role": "Divisional Forest Officer Meerut",
            "official_email": "dfo.meerut.forest@up.gov.in",
            "official_phone": "+911211040404",
            "portal_url": "https://upforest.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 1),
            "source_url": "https://upforest.gov.in/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Uttar Pradesh",
            "district": "Meerut",
            "authority_type": "PLANT_EMERGENCY",
            "department": "Meerut Industrial Area Safety Commission",
            "role": "Chief Industrial Safety Inspector Meerut",
            "official_email": "safety.meerut@up.gov.in",
            "official_phone": "+911211050505",
            "portal_url": "https://upindustrial.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 1),
            "source_url": "https://upindustrial.gov.in/contacts"
        },

        # --- Punjab ---
        {
            "id": uuid.uuid4(),
            "state": "Punjab",
            "district": "Bathinda",
            "authority_type": "FIRE_RESPONSE",
            "department": "Punjab Fire Services",
            "role": "District Fire Officer Bathinda",
            "official_email": "dfo.bathinda@punjabfire.gov.in",
            "official_phone": "+911641010101",
            "portal_url": "https://punjabfire.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 15),
            "source_url": "https://punjab.gov.in/departments"
        },
        {
            "id": uuid.uuid4(),
            "state": "Punjab",
            "district": "Bathinda",
            "authority_type": "POLLUTION_CONTROL",
            "department": "Punjab Pollution Control Board (PPCB)",
            "role": "Environmental Engineer PPCB Bathinda",
            "official_email": "ee.bathinda@ppcb.gov.in",
            "official_phone": "+911641020202",
            "portal_url": "https://ppcb.punjab.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 15),
            "source_url": "https://ppcb.punjab.gov.in/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Punjab",
            "district": "Bathinda",
            "authority_type": "DISTRICT_EMERGENCY",
            "department": "District Emergency Operations Centre Bathinda",
            "role": "Deputy Commissioner Bathinda",
            "official_email": "dc.bathinda@punjab.gov.in",
            "official_phone": "+911641030303",
            "portal_url": "https://bathinda.nic.in",
            "active": True,
            "verified_on": date(2026, 8, 15),
            "source_url": "https://bathinda.nic.in/directory"
        },
        {
            "id": uuid.uuid4(),
            "state": "Punjab",
            "district": "Bathinda",
            "authority_type": "FOREST_RESPONSE",
            "department": "Punjab Forest Department",
            "role": "Divisional Forest Officer Bathinda",
            "official_email": "dfo.bathinda.forest@punjab.gov.in",
            "official_phone": "+911641040404",
            "portal_url": "https://pbforests.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 15),
            "source_url": "https://pbforests.gov.in/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Punjab",
            "district": "Bathinda",
            "authority_type": "PLANT_EMERGENCY",
            "department": "Bathinda Industrial Development Corporation",
            "role": "Industrial Area Manager Bathinda",
            "official_email": "manager.bathindaind@punjab.gov.in",
            "official_phone": "+911641050505",
            "portal_url": "https://pbindustrial.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 15),
            "source_url": "https://pbindustrial.gov.in/contacts"
        },

        # --- Karnataka ---
        {
            "id": uuid.uuid4(),
            "state": "Karnataka",
            "district": "Chikkamagaluru",
            "authority_type": "FIRE_RESPONSE",
            "department": "Karnataka State Fire and Emergency Services (KSFES)",
            "role": "District Fire Officer Chikkamagaluru",
            "official_email": "dfo.ckm@ksfes.gov.in",
            "official_phone": "+918261010101",
            "portal_url": "https://ksfes.karnataka.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 10),
            "source_url": "https://karnataka.gov.in/directory"
        },
        {
            "id": uuid.uuid4(),
            "state": "Karnataka",
            "district": "Chikkamagaluru",
            "authority_type": "POLLUTION_CONTROL",
            "department": "Karnataka State Pollution Control Board (KSPCB)",
            "role": "Regional Officer KSPCB Chikkamagaluru",
            "official_email": "ro.ckm@kspcb.gov.in",
            "official_phone": "+918261020202",
            "portal_url": "https://kspcb.karnataka.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 10),
            "source_url": "https://kspcb.karnataka.gov.in/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Karnataka",
            "district": "Chikkamagaluru",
            "authority_type": "DISTRICT_EMERGENCY",
            "department": "District Emergency Operations Centre Chikkamagaluru",
            "role": "Deputy Commissioner Chikkamagaluru",
            "official_email": "dc.ckm@karnataka.gov.in",
            "official_phone": "+918261030303",
            "portal_url": "https://chikkamagaluru.nic.in",
            "active": True,
            "verified_on": date(2026, 8, 10),
            "source_url": "https://chikkamagaluru.nic.in/directory"
        },
        {
            "id": uuid.uuid4(),
            "state": "Karnataka",
            "district": "Chikkamagaluru",
            "authority_type": "FOREST_RESPONSE",
            "department": "Karnataka Forest Department",
            "role": "Deputy Conservator of Forests Chikkamagaluru",
            "official_email": "dcf.ckm@karnatakaforest.gov.in",
            "official_phone": "+918261040404",
            "portal_url": "https://aranya.gov.in",
            "active": True,
            "verified_on": date(2026, 8, 10),
            "source_url": "https://aranya.gov.in/contacts"
        },
        {
            "id": uuid.uuid4(),
            "state": "Karnataka",
            "district": "Chikkamagaluru",
            "authority_type": "PLANT_EMERGENCY",
            "department": "Karanataka Industrial Areas Development Board (KIADB)",
            "role": "Executive Engineer KIADB Chikkamagaluru",
            "official_email": "ee.ckm@kiadb.in",
            "official_phone": "+918261050505",
            "portal_url": "https://kiadb.in",
            "active": True,
            "verified_on": date(2026, 8, 10),
            "source_url": "https://kiadb.in/contacts"
        }
    ]

    for item in seed_data:
        auth = Authority(**item)
        session.add(auth)

    session.commit()
    print(f"Successfully seeded {len(seed_data)} authorities!")
    session.close()

if __name__ == "__main__":
    seed()
