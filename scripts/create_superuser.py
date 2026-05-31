"""Create an admin user from the command line.

Usage:
    python scripts/create_superuser.py --email admin@example.com --password secret123
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import SessionLocal  # noqa: E402
from app.services import auth_service  # noqa: E402


async def main(email: str, password: str, full_name: str | None) -> None:
    async with SessionLocal() as db:
        existing = await auth_service.get_user_by_email(db, email)
        if existing:
            print(f"User {email} already exists.")
            return
        user = await auth_service.register_user(db, email, password, full_name)
        print(f"Created user {user.email} ({user.id})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--full-name", default=None)
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password, args.full_name))
