# OSCAR NFR Baseline

Version: 1.0
Status: Baseline architecture and governance document
Scope: OSCAR HD-013.2D

This baseline defines the minimum non-functional requirements for the current OSCAR product phase. It is intentionally conservative and references [OSCAR Architecture V2](../OSCAR_ARCHITECTURE_V2.md) as the primary architectural source of truth.

## Scope And Reading Rules

- Current Requirement: applies to the repository as it exists today.
- Target: the desired operating expectation for the current product phase.
- Future / Planned: production-readiness work that is not yet implemented.
- If a numeric value cannot be justified from the repository or product requirements, the target remains: Target to be established during production-readiness phase.

## Baseline Summary

| Area | Current Requirement | Target | Future / Planned |
|---|---|---|---|
| Performance | Keep API and domain work bounded, deterministic where possible, and suitable for local operator use. | API latency target to be established during production-readiness phase. Scanner, decision, and execution-preparation latency targets to be established during production-readiness phase. | Add production SLOs after load and usage baselines exist. |
| Throughput | Support the current local/operator workflow and repository-backed processing model. | Request-volume target to be established during production-readiness phase. Market-data processing and concurrency targets to be established during production-readiness phase. | Define capacity limits after deployment model is chosen. |
| Availability | Development, research, and paper-trading workflows should remain usable even when some market or broker dependencies are unavailable. | Current product phase does not justify a hard institutional uptime SLA. Target to be established during production-readiness phase. | Production SLA to be introduced only when live trading is formally enabled. |
| Reliability | Fail loudly on invalid inputs, missing market data, or unavailable broker/context data; do not silently accept incomplete execution prep. | Deterministic behavior for calculators, validators, scanners, ranking, and persistence contracts. Recovery and retry expectations to be established during production-readiness phase. | Add explicit retry, backoff, and operational failure policies where justified. |
| Data Integrity | Preserve durable scanner and journal state; keep opportunity derived; avoid silent data loss. | Idempotency and transaction expectations to be defined per write path before production live use. Consistency must remain explicit across scanner, journal, and analytics flows. | Introduce stronger transaction and recovery policy if workload grows beyond local SQLite limits. |
| Observability | Emit structured, human-readable logs and expose health/readiness endpoints. | Correlation/request identifiers, richer audit metadata, and error visibility requirements to be established during production-readiness phase. | Expand observability only when there is a defined operational owner and deployment target. |
| Maintainability | Keep domains modular, typed, testable, and aligned with the architecture docs and ADRs. | Maintain API compatibility within the current versioning policy. Test coverage expectations to remain high for pure logic and contract surfaces. | Add versioned compatibility windows if external consumers appear. |
| Scalability | Continue using the current SQLite/local architecture as the foundation. Avoid premature distributed architecture. | Migration path to a stronger relational backend remains future-planned, not required now. | Reassess persistence and deployment scaling only when product demand proves it necessary. |

## Detailed Requirements

### 1. Performance

Current Requirement:

- API handlers should stay responsive enough for local operator use and should not perform unnecessary blocking work.
- Scanner, decision, and execution-preparation computations should remain deterministic and bounded by the current single-process workflow.
- Pure calculators and validators should stay fast enough to support synchronous request handling.

Target:

- API latency target to be established during production-readiness phase.
- Scanner processing target to be established during production-readiness phase.
- Decision pipeline target to be established during production-readiness phase.
- Execution preparation target to be established during production-readiness phase.

Future / Planned:

- Add measured SLOs only after the deployment pattern and expected usage are known.

### 2. Throughput

Current Requirement:

- Support the current operator workflow and local development usage.
- Market-data processing is limited by the current local MT5-backed architecture.
- Concurrency assumptions remain conservative and single-node oriented.

Target:

- Expected request volume to be established during production-readiness phase.
- Market-data processing target to be established during production-readiness phase.
- Concurrency target to be established during production-readiness phase.

Future / Planned:

- Introduce throughput engineering only after the runtime environment and traffic envelope are defined.

### 3. Availability

Current Requirement:

- Development and research workflows should remain usable without requiring production-grade infrastructure.
- Paper-trading and preparation flows should fail safely when the market feed or broker connection is not healthy.

Target:

- No institutional availability target is justified by the repository today.
- Target to be established during production-readiness phase.

Future / Planned:

- Separate availability expectations by environment only after live deployment is formally introduced.

### 4. Reliability

Current Requirement:

- Deterministic components must return reproducible results for the same inputs where the repository design allows it.
- Invalid or incomplete inputs must produce explicit failures or review states rather than silent success.
- Missing market data, broker metadata, or execution context must not be hidden.

Target:

- Recovery expectations to be established during production-readiness phase.
- Retry policy and failure-classification policy to be established during production-readiness phase.

Future / Planned:

- Add explicit operational recovery guidance for live environments.

### 5. Data Integrity

Current Requirement:

- Scanner snapshots and journal entries must remain durable where persistence is implemented.
- Opportunity remains derived state and must not become an independent source of truth.
- Journal entries must preserve decision snapshots and outcome history.
- State transitions must not silently overwrite or discard persisted records.

Target:

- Idempotency requirements for write APIs to be established during production-readiness phase.
- Transaction expectations for multi-step persistence flows to be established during production-readiness phase.
- Consistency requirements across scanner, journal, and analytics writes to be formalized before production use.

Future / Planned:

- Expand durable persistence rules only if the current SQLite foundation becomes insufficient.

### 6. Observability

Current Requirement:

- Use structured, timestamped application logging for operator and diagnostic visibility.
- Keep health and readiness endpoints available for runtime inspection.
- Surface validation failures and broker-facing errors clearly in API responses.

Target:

- Correlation/request identifier support to be established during production-readiness phase.
- Auditability requirements to be established during production-readiness phase.
- Error-visibility thresholds to be established during production-readiness phase.

Future / Planned:

- Add richer telemetry only after the operational operating model is defined.

### 7. Maintainability

Current Requirement:

- Preserve the modular domain structure and typed API contracts.
- Keep calculation, validation, and ranking logic testable in isolation.
- Keep architecture documentation and ADRs synchronized with implemented behavior.
- Maintain API compatibility within the documented versioning policy.

Target:

- Test coverage expectations to remain high for domain logic and contract surfaces.
- Documentation completeness to remain high for any architectural boundary or product contract.

Future / Planned:

- Introduce compatibility windows or deprecation plans only if external consumers require them.

### 8. Scalability

Current Requirement:

- The current SQLite/local architecture remains the supported baseline.
- The system should avoid distributed or cloud architecture until it is actually required.

Target:

- Migration path to a stronger relational backend to be established only when production-readiness planning justifies it.
- Horizontal scaling is not a current requirement.

Future / Planned:

- Revisit the persistence and deployment model when current-local limits are reached.

## Repository-Aligned Notes

- Scanner is the durable snapshot source of truth.
- Opportunity is derived from scanner snapshots.
- Journal is the durable source of truth for recorded decisions and outcomes.
- Execution Bridge remains prepare-only in the current architecture.
- The repository does not currently justify a production SLA, production traffic envelope, or institutional latency target.

## Explicit Non-Goals For This Phase

- No distributed infrastructure requirement.
- No cloud infrastructure requirement.
- No production monitoring platform requirement.
- No live-execution reliability target.
- No production-readiness SLA claim.
