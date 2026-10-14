# Workflow specification

## State model

| State | Meaning | Next events |
|---|---|---|
| `offer_accepted` | Candidate accepted; onboarding not yet started | `documents_submitted`, `deadline_changed` |
| `documents_pending` | Candidate action required for documents | `documents_submitted`, `deadline_at_risk` |
| `drug_test_pending` | Appointment or verified completion pending | `drug_test_scheduled`, `drug_test_completed`, `deadline_at_risk` |
| `screening_pending` | Awaiting authorized screening status | `screening_cleared`, `deadline_at_risk` |
| `ready_to_start` | Required steps reported complete by trusted sources | terminal for this workflow |
| `exception` | Human intervention required | authorized staff resolve and resume |

The demo starts in `offer_accepted`; a production system should model each requirement independently because steps can overlap.

## Event contract

Every event must have a unique ID, candidate reference, event type, timestamp, and validated details. Replayed events must not create duplicate side effects.

Suggested production events:
- `offer_accepted`
- `instructions_sent`
- `candidate_acknowledged`
- `appointment_options_offered`
- `drug_test_scheduled`
- `drug_test_completed` (trusted provider/authorized staff only)
- `i9_step_completed` (never infer from uploaded file alone)
- `screening_status_updated` (minimum necessary status only)
- `deadline_changed`
- `deadline_at_risk`
- `candidate_requested_help`
- `candidate_requested_accommodation`
- `human_review_completed`

## Reminder policy

1. Initial message states the exact action, deadline, official help link, and approved portal.
2. If an appointment is confirmed, stop appointment-chasing messages.
3. Reminders are sent only when a step remains incomplete, a deadline exists, and the reminder is within contact hours.
4. Apply a cooldown and strict per-step reminder cap.
5. If a deadline is at risk, escalate to a human instead of sending repeated messages.
6. Respect communication preferences, opt-outs where applicable, accommodations, and applicable laws.
7. Never represent a requested completion date as a legal deadline unless the responsible authority has established it.

## Concise templates

**Action required**
> Hi {first_name}, please complete {step} by {deadline}. Instructions: {official_link}. Secure portal: {approved_portal}. Reply if you encounter a problem.

**Appointment recorded**
> Thanks, we've recorded your appointment for {date/time}. Please follow the provider's instructions. We'll contact you if anything changes.

**Exception**
> We may need help resolving a scheduling issue before the deadline. Please contact {human_contact} at {contact_method}. No action is required beyond the steps listed here.

## AI boundary

An LLM may summarize instructions from an approved source, draft accessible messages, classify non-sensitive support requests, or suggest a next step. Deterministic code and authorized systems must control deadlines, permissions, status transitions, and notifications. Human review is required for adverse actions, ambiguous compliance questions, accommodations, disputes, and exceptions.
