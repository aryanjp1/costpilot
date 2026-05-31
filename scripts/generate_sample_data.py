"""Generate 30 days of realistic demo events and POST them to the ingest API.

Usage:
    python scripts/generate_sample_data.py \
        --api-key cp_proj_xxx \
        --endpoint http://localhost:8787
"""
import argparse
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.utils.pricing import calculate_cost  # noqa: E402

MODELS = (
    ["gpt-4o"] * 6
    + ["claude-sonnet-4-6"] * 2
    + ["gpt-4o-mini"] * 1
    + ["deepseek-chat", "claude-opus-4-7"]
)
FEATURES = ["doc-summary", "chat", "search", "classify", "translate"]
USERS = ["alice", "bob", "carol", "dave", "erin"]


def _make_event(when: datetime) -> dict:
    model = random.choice(MODELS)
    input_tokens = random.randint(200, 6000)
    output_tokens = random.randint(50, 1500)
    is_error = random.random() < 0.05
    latency = random.randint(300, 4000)

    if is_error:
        return {
            "model": model,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "latency_ms": latency,
            "status": "error",
            "error_message": random.choice(
                ["rate_limit_exceeded", "context_length_exceeded", "timeout"]
            ),
            "tags": {"feature": random.choice(FEATURES), "user": random.choice(USERS)},
            "timestamp": when.isoformat(),
        }

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(calculate_cost(model, input_tokens, output_tokens), 6),
        "latency_ms": latency,
        "status": "success",
        "tags": {"feature": random.choice(FEATURES), "user": random.choice(USERS)},
        "timestamp": when.isoformat(),
    }


def generate(days: int) -> list[dict]:
    events = []
    now = datetime.now(timezone.utc)
    for day in range(days):
        day_start = now - timedelta(days=day)
        # Usage grows toward the present, so recent days get more requests.
        growth = 1.0 + (days - day) / days
        spike = 2.5 if random.random() < 0.1 else 1.0
        count = max(50, int(random.randint(120, 300) * growth * spike))
        for _ in range(count):
            when = day_start - timedelta(
                hours=random.randint(0, 23), minutes=random.randint(0, 59)
            )
            events.append(_make_event(when))
    return events


def send(events: list[dict], endpoint: str, api_key: str, batch_size: int = 100):
    headers = {"Authorization": f"Bearer {api_key}"}
    sent = 0
    with httpx.Client(timeout=30.0) as client:
        for i in range(0, len(events), batch_size):
            batch = events[i : i + batch_size]
            resp = client.post(
                f"{endpoint.rstrip('/')}/api/ingest",
                json={"events": batch},
                headers=headers,
            )
            resp.raise_for_status()
            sent += resp.json()["accepted"]
            print(f"  sent {sent}/{len(events)}")
    return sent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--endpoint", default="http://localhost:8787")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    print(f"Generating ~{args.days} days of events...")
    events = generate(args.days)
    random.shuffle(events)
    print(f"Generated {len(events)} events. Uploading...")
    total = send(events, args.endpoint, args.api_key)
    print(f"Done. {total} events ingested.")


if __name__ == "__main__":
    main()
