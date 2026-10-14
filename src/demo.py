"""Run a synthetic onboarding example; no real messages are sent."""
from datetime import datetime, timedelta, timezone
from .workflow import Candidate, Event, Workflow


def main():
    sent = []
    workflow = Workflow(send=sent.append)
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    candidate = Candidate("DEMO-001", "Alex", deadline=now + timedelta(days=2))
    workflow.add_candidate(candidate)

    workflow.handle(Event("evt-1", "DEMO-001", "documents_submitted", now))
    workflow.handle(Event(
        "evt-2", "DEMO-001", "drug_test_scheduled", now,
        {"appointment_at": now + timedelta(days=1, hours=2)},
    ))
    print(f"Candidate state: {candidate.state.value}")
    print(f"Notifications queued: {len(sent)}")
    for n in sent:
        print(f"\n[{n.channel}] {n.subject}\n{n.body}")


if __name__ == "__main__":
    main()
