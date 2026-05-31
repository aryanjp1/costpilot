"""End-to-end seed: create a demo user, project, API key, and sample events.

Run after the database is up (docker compose up -d db) and migrations applied.

Usage:
    python scripts/seed.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import SessionLocal  # noqa: E402
from app.services import auth_service, project_service  # noqa: E402

import generate_sample_data  # noqa: E402

DEMO_EMAIL = "demo@costpilot.dev"
DEMO_PASSWORD = "costpilot-demo"
ENDPOINT = "http://localhost:8787"


async def main() -> None:
    async with SessionLocal() as db:
        user = await auth_service.get_user_by_email(db, DEMO_EMAIL)
        if user is None:
            user = await auth_service.register_user(
                db, DEMO_EMAIL, DEMO_PASSWORD, "Demo User"
            )
            print(f"Created demo user {DEMO_EMAIL} / {DEMO_PASSWORD}")

        projects = await project_service.list_projects_for_user(db, user)
        if projects:
            project = projects[0]
        else:
            project = await project_service.create_project(
                db, user, "Demo Project", "Seeded sample workspace"
            )
            print(f"Created project {project.name}")

        _, full_key = await project_service.create_api_key(db, project.id, "Seed Key")
        print(f"API key: {full_key}")

    print("Generating sample events...")
    events = generate_sample_data.generate(30)
    generate_sample_data.send(events, ENDPOINT, full_key)
    print("Seed complete. Log in at http://localhost:3000")


if __name__ == "__main__":
    asyncio.run(main())
