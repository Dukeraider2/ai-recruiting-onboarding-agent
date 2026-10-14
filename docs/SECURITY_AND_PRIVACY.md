# Security and privacy requirements

This prototype is not approved for real candidate data.

## Data minimization
- Store workflow state, event IDs, deadline timestamps, and non-sensitive references only.
- Never store document images, Social Security numbers, full identity-document numbers, medical details, or drug-test results in application logs, prompts, analytics, or source control.
- Keep sensitive documents inside the employer's approved I-9 / screening provider system.
- Send clients only the minimum authorized status information.

## Access control
- Authenticate candidate and staff access.
- Apply least-privilege, role-based access and tenant isolation.
- Require MFA for staff and privileged actions.
- Use short-lived, scoped upload links; never expose a shared folder to unintended recipients.
- Separate development, test, and production environments.

## Reliability and auditability
- Use durable event storage and idempotency keys.
- Record who/what changed a status, when, and the authoritative source.
- Avoid writing sensitive payloads to audit logs.
- Monitor retries, failed deliveries, webhook signatures, and dead-letter queues.
- Provide retention and deletion policies reviewed by counsel.

## AI safety
- Treat candidate-provided text and uploaded content as untrusted input.
- Do not let prompts override policy, grant access, alter deadlines, or mark checks complete.
- Do not ask an LLM to infer protected characteristics or decide eligibility, drug-test outcomes, or adverse actions.
- Use approved knowledge sources and cite the source in staff-facing answers.
- Test for prompt injection, data leakage, disparate impact, hallucinated deadlines, and incorrect escalation.

## Compliance review
Before production, qualified HR, employment counsel, privacy, security, and accessibility specialists must review the system against applicable federal, state, and local requirements, including Form I-9, E-Verify where applicable, drug-screening rules, record retention, notice/consent, and candidate accommodation processes.
