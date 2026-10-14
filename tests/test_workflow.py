import unittest
from datetime import datetime, timedelta, timezone
from src.workflow import Candidate, Event, State, Workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 14, 16, 0, tzinfo=timezone.utc)
        self.sent = []
        self.w = Workflow(send=self.sent.append, contact_start_hour=8, contact_end_hour=18)
        self.c = Candidate("C-1", "Alex", deadline=self.now + timedelta(days=2))
        self.w.add_candidate(self.c)

    def event(self, eid, kind, details=None):
        self.w.handle(Event(eid, "C-1", kind, self.now, details or {}))

    def test_documents_submitted_advances_state(self):
        self.event("1", "documents_submitted")
        self.assertEqual(self.c.state, State.DRUG_TEST_PENDING)

    def test_duplicate_event_is_idempotent(self):
        self.event("1", "documents_submitted")
        self.event("1", "documents_submitted")
        self.assertEqual(self.c.state, State.DRUG_TEST_PENDING)

    def test_appointment_confirmation_sends_one_message(self):
        self.event("2", "drug_test_scheduled", {"appointment_at": self.now + timedelta(days=1)})
        self.assertEqual(len(self.sent), 1)
        self.event("2", "drug_test_scheduled", {"appointment_at": self.now + timedelta(days=1)})
        self.assertEqual(len(self.sent), 1)

    def test_reminder_suppressed_outside_contact_hours(self):
        self.assertFalse(self.w.evaluate_reminder(
            "C-1", self.now.replace(hour=6), "I-9 step",
            "https://example.invalid/instructions"
        ))
        self.assertEqual(len(self.sent), 0)

    def test_reminder_has_cooldown_and_cap(self):
        self.assertTrue(self.w.evaluate_reminder(
            "C-1", self.now, "onboarding step", "https://example.invalid/instructions"
        ))
        self.assertFalse(self.w.evaluate_reminder(
            "C-1", self.now + timedelta(hours=2), "onboarding step",
            "https://example.invalid/instructions"
        ))
        self.assertTrue(self.w.evaluate_reminder(
            "C-1", self.now + timedelta(days=1, hours=1), "onboarding step",
            "https://example.invalid/instructions"
        ))
        self.assertFalse(self.w.evaluate_reminder(
            "C-1", self.now + timedelta(days=1, hours=2), "onboarding step",
            "https://example.invalid/instructions"
        ))

    def test_verified_completion_advances_to_screening(self):
        self.event("3", "drug_test_completed")
        self.assertEqual(self.c.state, State.SCREENING_PENDING)

    def test_risk_escalates_to_human(self):
        self.event("4", "deadline_at_risk", {"reason": "Provider appointment unavailable"})
        self.assertEqual(self.c.state, State.EXCEPTION)
        self.assertIsNotNone(self.c.exception_reason)

    def test_unknown_candidate_rejected(self):
        with self.assertRaises(KeyError):
            self.w.handle(Event("x", "missing", "documents_submitted", self.now))


if __name__ == "__main__":
    unittest.main()
