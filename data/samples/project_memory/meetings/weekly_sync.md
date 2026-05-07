# Weekly Sync - May 7

## Status: Sprint 3 is on track

## Decision: Use Postgres for event store
We decided to use Postgres instead of MongoDB for the event store.

## Decision: Delay payment integration to Sprint 5
The payment gateway API has breaking changes, delaying integration.

## Blocker: Staging environment is down
The staging env needs DNS config update before QA can continue.

## Risk: Third-party email API rate limit
We are approaching the 10k/day SendGrid limit for transactional emails.

- [x] TASK: Design event store schema
- [ ] TASK: Create event store migration
- [ ] TASK: Implement event store writer
- Owner: Alice event store service
- Owner: Bob frontend dashboard
- Q: When is the CI upgrade scheduled?
- Q: Do we need GDPR consent for event store?
- Deadline: Sprint 3 end - May 14
- Follow-up: Check SendGrid rate limit increase with ops
- Note: Retrospective is scheduled for Friday 4pm
