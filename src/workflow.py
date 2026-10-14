"""Minimal event-driven onboarding workflow prototype.

Uses only synthetic metadata. Do not store sensitive documents or test results here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable


class State(str, Enum):
    OFFER_ACCEPTED = "offer_accepted"
    DOCUMENTS_PENDING = "documents_pending"
    DRUG_TEST_PENDING = "drug_test_pending"
    SCREENING_PENDING = "screening_pending"
    READY_TO_START = "ready_to_start"
    EXCEPTION = "exception"


@dataclass
class Candidate:
    candidate_id: str
    first_name: str
    state: State = State.OFFER_ACCEPTED
    deadline: datetime | None = None
    appointment_at: datetime | None = None
    last_reminder_at: datetime | None = None
    reminder_count: int = 0
    completed_steps: set[str] = field(default_factory=set)
    exception_reason: str | None = None


@dataclass(frozen=True)
class Event:
    event_id: str
    candidate_id: str
    kind: str
    occurred_at: datetime
    details: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Notification:
    candidate_id: str
    channel: str
    subject: str
    body: str
    idempotency_key: str


class Workflow:
    """A deterministic workflow engine with replaceable notification sink."""

    def __init__(
        self,
        send: Callable[[Notification], None] | None = None,
        contact_start_hour: int = 8,
        contact_end_hour: int = 18,
        minimum_reminder_gap: timedelta = timedelta(hours=24),
        max_reminders_per_step: int = 2,
    ):
        self.candidates: dict[str, Candidate] = {}
        self.processed_events: set[str] = set()
        self.sent_keys: set[str] = set()
        self.audit: list[dict] = []
        self.send = send or (lambda notification: None)
        self.contact_start_hour = contact_start_hour
        self.contact_end_hour = contact_end_hour
        self.minimum_reminder_gap = minimum_reminder_gap
        self.max_reminders_per_step = max_reminders_per_step

    def add_candidate(self, candidate: Candidate) -> None:
        if candidate.candidate_id in self.candidates:
            raise ValueError("candidate_id already exists")
        self.candidates[candidate.candidate_id] = candidate
        self._log("candidate_created", candidate.candidate_id, candidate.state.value)

    def handle(self, event: Event) -> None:
        if event.event_id in self.processed_events:
            self._log("duplicate_event_ignored", event.candidate_id, event.event_id)
            return
        candidate = self.candidates.get(event.candidate_id)
        if not candidate:
            raise KeyError("Unknown candidate_id")
        self.processed_events.add(event.event_id)
        self._log("event_received", candidate.candidate_id, event.kind)

        if event.kind == "documents_submitted":
            candidate.completed_steps.add("documents_submitted")
            candidate.state = State.DRUG_TEST_PENDING
        elif event.kind == "drug_test_scheduled":
            when = event.details.get("appointment_at")
            if not isinstance(when, datetime):
                raise ValueError("appointment_at datetime required")
            candidate.appointment_at = when
            candidate.state = State.DRUG_TEST_PENDING
            self._notify(
                candidate, "email", "Drug test appointment recorded",
                f"Hi {candidate.first_name}, we've recorded your appointment. "
                "Please follow the testing provider's instructions. We'll contact you "
                "if anything changes or the deadline is at risk.",
                f"{candidate.candidate_id}:appointment:{when.isoformat()}",
            )
        elif event.kind == "drug_test_completed":
            # Completion is accepted only from a trusted integration or authorized staff.
            candidate.completed_steps.add("drug_test_completed")
            candidate.state = State.SCREENING_PENDING
            candidate.appointment_at = None
        elif event.kind == "screening_cleared":
            candidate.completed_steps.add("screening_cleared")
            candidate.state = State.READY_TO_START
            candidate.deadline = None
        elif event.kind == "deadline_at_risk":
            candidate.state = State.EXCEPTION
            candidate.exception_reason = str(event.details.get("reason", "Deadline at risk"))
            self._log("human_review_required", candidate.candidate_id, candidate.exception_reason)
        elif event.kind == "deadline_changed":
            deadline = event.details.get("deadline")
            if not isinstance(deadline, datetime):
                raise ValueError("deadline datetime required")
            candidate.deadline = deadline
        else:
            raise ValueError(f"Unsupported event kind: {event.kind}")

        self._log("state_changed", candidate.candidate_id, candidate.state.value)

    def evaluate_reminder(self, candidate_id: str, now: datetime, step: str,
                          instruction_url: str, upload_url: str | None = None) -> bool:
        """Send at most a bounded reminder when due; never send outside contact hours."""
        c = self.candidates[candidate_id]
        if c.state in (State.READY_TO_START, State.EXCEPTION):
            return False
        if c.deadline is None or now >= c.deadline:
            if c.deadline is not None and now >= c.deadline:
                c.state = State.EXCEPTION
                c.exception_reason = f"{step} deadline reached without verified completion"
                self._log("human_review_required", c.candidate_id, c.exception_reason)
            return False
        if not (self.contact_start_hour <= now.hour < self.contact_end_hour):
            return False
        if c.reminder_count >= self.max_reminders_per_step:
            return False
        if c.last_reminder_at and now - c.last_reminder_at < self.minimum_reminder_gap:
            return False

        body = (f"Hi {c.first_name}, this is a reminder to complete {step} by "
                f"{c.deadline.strftime('%Y-%m-%d %H:%M %Z')}. "
                f"Instructions: {instruction_url}")
        if upload_url:
            body += f"\nSecure submission portal: {upload_url}"
        body += "\nReply if you encounter a problem or need an accommodation."
        key = f"{c.candidate_id}:{step}:reminder:{c.reminder_count + 1}"
        sent = self._notify(c, "email", f"Action required: {step}", body, key)
        if sent:
            c.reminder_count += 1
            c.last_reminder_at = now
            self._log("reminder_sent", c.candidate_id, step)
        return sent

    def _notify(self, c: Candidate, channel: str, subject: str, body: str, key: str) -> bool:
        if key in self.sent_keys:
            self._log("duplicate_notification_suppressed", c.candidate_id, key)
            return False
        notification = Notification(c.candidate_id, channel, subject, body, key)
        self.send(notification)
        self.sent_keys.add(key)
        return True

    def _log(self, action: str, candidate_id: str, detail: str) -> None:
        self.audit.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "candidate_id": candidate_id,
            "detail": detail,
        })
