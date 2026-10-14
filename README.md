# AI Recruiting & Onboarding Workflow Agent

A practical reference implementation for reducing repetitive candidate follow-ups through event-driven workflow automation.

**Goal:** send clear instructions, track verified workflow state, issue proportionate reminders, and escalate genuine exceptions rather than repeatedly contacting candidates.

> This repository is a prototype and design reference, not a production HR/compliance system. Use synthetic data only. Do not place real I-9 documents, Social Security numbers, drug-test results, identity documents, or other sensitive candidate information in this project.

## What it does

- Models onboarding as explicit states: `offer_accepted`, `documents_pending`, `drug_test_pending`, `screening_pending`, `ready_to_start`, `exception`.
- Sends concise, templated notifications through a replaceable notification adapter.
- Avoids duplicate reminders with idempotency keys and a notification log.
- Tracks deadlines and escalates exceptions rather than generating endless follow-ups.
- Keeps sensitive documents in an approved external system; stores references/status only.
- Requires verified events from authorized systems before marking steps complete.
- Provides a human-review path for consequential or ambiguous cases.

## Architecture

```text
ATS / HRIS / screening provider
             |
             v
     Event intake + validation
             |
             v
   Candidate workflow state machine
             |
       +-----+------+
       |            |
       v            v
 Rules / timers   Audit event log
       |
       v
 Notification adapter -----> Email/SMS provider
       |
       v
 Human exception queue ----> Recruiter / HR
```

## Candidate experience

1. Candidate receives one concise message with the requirement, deadline, official instructions, and approved secure portal.
2. Candidate confirms an appointment or submits the required step.
3. System records the confirmation and sends a single status update to authorized stakeholders.
4. A reminder is sent only when needed and within configured contact hours.
5. If a deadline is at risk, the workflow creates an exception for a human to resolve.

## Quick start

Requires Python 3.11 or newer. No third-party packages are required for the demo.

```bash
python -m unittest discover -s tests -v
python -m src.demo
```

The demo uses fictional candidate data and prints notifications instead of sending real messages.

## Repository layout

- `docs/WORKFLOW.md`: states, events, timing, and exception handling
- `docs/SECURITY_AND_PRIVACY.md`: data minimization and security controls
- `docs/IMPLEMENTATION_PLAN.md`: phased path to production
- `src/workflow.py`: small event-driven workflow engine
- `src/demo.py`: synthetic end-to-end example
- `tests/test_workflow.py`: tests for transitions, reminders, and idempotency
- `config.example.json`: example policy configuration
- `.github/workflows/tests.yml`: CI test workflow

## Design principles

- **Deadlines are explicit:** do not invent a more urgent deadline than the one authorized by policy.
- **One request, one confirmation:** once a candidate confirms a plan, avoid repetitive messages unless something changes.
- **State beats guesswork:** use trusted system events, not an LLM's inference, to mark compliance tasks complete.
- **AI drafts; rules control:** an LLM may draft plain-language messages, but deterministic policy controls deadlines, permissions, and transitions.
- **Human accountability:** exceptions, adverse decisions, and ambiguous cases go to authorized staff.
- **Privacy by design:** this prototype stores no document contents or medical/test results.

## Important compliance note

This project does not provide legal advice and is not certified for employment compliance. Production deployments must be reviewed by qualified HR, privacy, security, and legal teams. Follow applicable requirements for Form I-9, E-Verify, drug screening, record retention, accessibility, consent, and candidate communications. Do not use an AI model to determine work authorization, interpret drug-test results, or make hiring/adverse-action decisions.

## License

MIT. See `LICENSE`.
