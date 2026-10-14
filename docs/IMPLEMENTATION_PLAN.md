# Implementation plan

## Phase 1: Prototype
- [x] Define states and event contract
- [x] Add concise notification templates
- [x] Add duplicate-event suppression
- [x] Add contact-hour guard, reminder cooldown, and reminder cap
- [x] Add synthetic-data tests and demo

## Phase 2: Controlled pilot
- Choose one ATS and one approved screening provider.
- Integrate through documented APIs/webhooks with signature verification.
- Use a transactional outbox and durable queue for notifications.
- Configure employer-approved deadlines, time zones, quiet hours, and message channels.
- Run in shadow mode first; compare suggested actions with human decisions.
- Pilot with synthetic or consented test accounts before limited production rollout.

## Phase 3: Production readiness
- Complete privacy/security threat model and legal review.
- Add authentication, RBAC, encryption, key management, tenant isolation, retention/deletion controls, and audit monitoring.
- Add delivery receipts, retry policy, dead-letter queue, and operational dashboards.
- Add accessibility and localization testing.
- Evaluate reminder burden, completion times, candidate satisfaction, error rate, missed deadlines, and human escalation rate.
- Monitor for disparate impact; provide human appeal and correction channels.

## Success metrics
- Median candidate completion time
- Number of manual recruiter touches per candidate
- Duplicate or contradictory messages
- Deadline misses caused by process failures
- Candidate support and satisfaction
- Security incidents and unauthorized data access
- Human exception resolution time

## Rollout guardrails
Do not auto-reject candidates, decide work authorization, interpret screening results, or make other consequential employment decisions. Automation may coordinate the process, but authorized people and trusted systems remain responsible for decisions.
