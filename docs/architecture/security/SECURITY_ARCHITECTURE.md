# OSCAR Security Architecture Baseline

Version: 1.0
Status: Baseline architecture and governance document
Scope: OSCAR HD-013.2D

This document defines the current security boundary and the minimum baseline expected for OSCAR. It references [OSCAR Architecture V2](../OSCAR_ARCHITECTURE_V2.md) and the execution ADRs as the governing architectural context.

## Scope And Rules

- Current state describes what the repository actually contains today.
- Required baseline describes the minimum control expectation for this phase.
- Future production requirement describes what should exist before live production use.
- This document does not implement authentication, authorization, OAuth, or live execution.

## Security Baseline Summary

| Area | Current State | Required Baseline | Future Production Requirement |
|---|---|---|---|
| Authentication | No authentication layer is present in the current backend API surface. | Keep the current boundary explicit: development and internal operator use only. | Introduce authentication before any production exposure. |
| Authorization | No authorization policy is implemented in the repository. | Do not imply role-based access control exists. Treat all exposed endpoints as trusted-local only. | Introduce authorization before any multi-user or production deployment. |
| Secrets Management | No dedicated secrets-management infrastructure exists in the repository. | Do not hard-code broker credentials or sensitive values into source files or docs. | Use an approved secrets-management strategy before production deployment. |
| Credential Handling | Broker and MT5 connectivity are accessed locally through the current runtime and not through a hardened secrets store. | Minimize credential exposure and avoid logging secrets. | Store and rotate credentials through production-grade controls before live use. |
| API Security | The API is versioned and composed locally, but there is no auth gateway or WAF layer. | Validate request payloads at the schema and domain levels. Keep error responses bounded and do not leak secrets. | Add authentication, authorization, rate controls, and external-edge protections before production. |
| Input Validation | Strong schema validation exists in several request models and execution validators. | Maintain validation at the API edge and again in domain services for trade and persistence paths. | Extend validation coverage for all external inputs before production exposure. |
| Output / Data Exposure | API responses may return detailed validation and operational information. | Do not expose secrets, credentials, or raw broker tokens. Limit data returned to the minimum useful set. | Apply stricter redaction and response shaping before production. |
| Audit Logging | Logging exists through the application logger, but no dedicated audit subsystem exists. | Preserve clear logs for trade preparation, validation outcomes, and failures. | Introduce an immutable audit trail for sensitive actions before production. |
| Sensitive Data Handling | Sensitive handling is not yet governed by a dedicated subsystem. | Keep account and broker metadata out of logs where possible. | Define redaction and retention rules before live trading. |
| Dependency Security | The repository does not define a formal dependency-scanning process in code. | Keep dependencies minimal and review changes that touch broker, network, or serialization paths carefully. | Add dependency review and vulnerability management before production. |
| Configuration Security | Settings are local and largely static in code, including debug-oriented defaults. | Treat runtime configuration as local-development configuration unless explicitly promoted. | Separate and harden production configuration before live use. |
| Execution Safety | The current execution bridge is prepare-only. A separate legacy trade API surface exists in the repository and must not be confused with the prepare-only baseline. | Prevent accidental live-trading assumptions. Require explicit human review for any execution-preparation result. | Any live execution capability must be gated, audited, and separately authorized before production. |
| Development vs Production Separation | The repository is currently oriented toward local development, research, and preparation workflows. | Keep production assumptions out of the current codebase and docs unless they are explicitly labeled future work. | Introduce explicit promotion controls before production. |

## 1. Authentication

Current State:

- No authentication is implemented on the current backend API surface.
- The repository does not include OAuth or a comparable identity layer.

Required Baseline:

- Keep the current repository scope limited to trusted local or internal operator use.
- Do not represent unauthenticated endpoints as production-safe.

Future Production Requirement:

- Introduce authentication before any external or shared production deployment.

## 2. Authorization

Current State:

- No role-based authorization model is implemented.

Required Baseline:

- Do not rely on implicit trust for production-sensitive actions.
- Treat the absence of authorization as a hard boundary against production use.

Future Production Requirement:

- Add explicit permission boundaries before live deployment or multi-user access.

## 3. Secrets Management

Current State:

- No secrets-management infrastructure is defined in the repository.

Required Baseline:

- Do not embed broker credentials, API keys, or access tokens in source-controlled code.
- Keep any required sensitive values out of logs, test fixtures, and documentation.

Future Production Requirement:

- Introduce an approved secrets-management process before production use.

## 4. Credential Handling

Current State:

- Broker connectivity is currently handled through local runtime integration.

Required Baseline:

- Avoid exposing account numbers, login identifiers, or broker metadata unnecessarily.
- Do not print secrets in exception traces or operational logs.

Future Production Requirement:

- Enforce credential rotation, secure storage, and least-privilege handling before live trading.

## 5. API Security

Current State:

- The API is versioned and exposed locally through FastAPI routers.
- There is no auth gateway, request-signing layer, or network perimeter control in the repository.

Required Baseline:

- Validate request payloads through Pydantic schemas and domain validators.
- Keep API responses small enough to support operator troubleshooting without exposing sensitive internals.
- Preserve the current API versioning policy.

Future Production Requirement:

- Add auth, rate limiting, edge controls, and response redaction before production exposure.

## 6. Input Validation

Current State:

- Execution request schemas enforce typed fields and value constraints.
- Execution preparation includes domain validation for risk, spread, lot size, stops, and margin.

Required Baseline:

- Continue validating at both the transport boundary and the domain boundary.
- Reject invalid or incoherent trade requests instead of normalizing them into success.

Future Production Requirement:

- Extend input validation coverage to all external entry points before production use.

## 7. Output And Data Exposure

Current State:

- API responses include detailed validation results and operational readiness information.

Required Baseline:

- Limit responses to what the operator needs to make a safe decision.
- Do not return credentials, secrets, or broker session material.

Future Production Requirement:

- Apply explicit redaction rules and response policies before production deployment.

## 8. Audit Logging

Current State:

- The logger emits timestamped application messages.
- There is no dedicated immutable audit store for sensitive actions.

Required Baseline:

- Preserve traceable logging for trade preparation failures, validation outcomes, and major state changes.
- Keep audit-relevant events distinguishable from general debug output.

Future Production Requirement:

- Introduce immutable execution and administrative audit logging before live use.

## 9. Sensitive Data Handling

Current State:

- Sensitive-data handling is not centralized in the repository.

Required Baseline:

- Do not log secrets, tokens, or credential payloads.
- Be careful with account metadata and broker messages because they may contain sensitive operational details.

Future Production Requirement:

- Define redaction, retention, and access rules before production deployment.

## 10. Dependency Security

Current State:

- No explicit dependency-security workflow is defined in the repository documentation.

Required Baseline:

- Keep dependency changes minimal and review any package that touches MT5, network IO, persistence, or validation.

Future Production Requirement:

- Add formal dependency review and vulnerability management before production.

## 11. Configuration Security

Current State:

- Configuration is currently local and code-backed, with debug-oriented defaults.

Required Baseline:

- Treat current settings as development and research defaults.
- Do not assume they are safe for production or live trading.

Future Production Requirement:

- Separate development and production configuration and lock down unsafe defaults before live use.

## 12. Execution Safety

Current State:

- The execution bridge is prepare-only.
- A separate trade API surface exists in the repository and should be treated as a legacy compatibility surface, not the architectural baseline for new work.

Required Baseline:

- Keep preparation and execution conceptually separate.
- Prevent accidental live-trading assumptions in documentation, UI wording, and operator workflow.
- Validate orders, risk, and margin before any execution-preparation result is accepted.

Future Production Requirement:

- Any live execution path must be separately gated, authorized, and audited before production deployment.

## 13. Development Vs Production Separation

Current State:

- The repository is aligned to development, research, and preparation workflows.

Required Baseline:

- Keep production controls out of the current baseline unless they are explicitly marked future work.
- Ensure that current docs do not imply production readiness.

Future Production Requirement:

- Introduce explicit promotion, environment, and approval controls before live use.

## Trading-Specific Security Requirements

- Prevent unauthorized execution by keeping live execution outside the current prepare-only bridge.
- Treat prepare-only results as decision support, not as a broker command path.
- Protect broker credentials and related metadata from source control, logs, and casual exposure.
- Validate order side, size, stops, spread, and margin before any execution-preparation result can be used.
- Keep risk-limit enforcement explicit and visible in the execution-preparation output.
- Maintain auditable traces of execution requests and validation failures.
- Reduce accidental live-trading risk by separating development, research, paper, and live concepts in both documentation and runtime workflow.

## Trust Boundaries

| Boundary | Trusted Side | Untrusted Side | Validation Required |
|---|---|---|---|
| Frontend -> Backend API | Backend API | Frontend input | Schema validation, type coercion checks, domain validation |
| Backend API -> Domain Engines | Domain engines once inputs are validated | API payloads and user-provided parameters | Execution, scanner, decision, and journal domain validation |
| Domain Engines -> Persistence | Persistence layer once contracts are validated | Domain write payloads | Repository validation, transaction discipline, consistency checks |
| Domain Engines -> Market Data | Local market service and broker feed adapters | External market feed responses | Presence checks, symbol checks, stale-data checks |
| Domain Engines -> Broker / Execution Layer | Controlled execution-preparation code | Broker responses and terminal metadata | Order validation, connection checks, margin/risk validation |
| Backend -> External Services | None by default beyond the local MT5/broker integration | Any external service or network dependency | Strict input/output validation and failure handling |
| Backend -> Local Development Environment | Local developer machine and launcher tooling | OS/process environment, local files, and runtime state | Configuration review, path handling, safe defaults |

## Environment Model

### DEVELOPMENT

- Permitted: local API startup, scanner review, decision reports, journal review, execution preparation, tests, and documentation work.
- Not permitted: assumptions of production authentication, production authorization, or live execution readiness.

### RESEARCH / BACKTEST

- Permitted: historical analysis, deterministic calculations, derived-state inspection, and replay-friendly workflows.
- Not permitted: claiming live reliability, live operational SLOs, or production-grade credential handling.

### PAPER TRADING

- Permitted: execution preparation and controlled validation of trade logic using non-live broker or simulation pathways if configured.
- Not permitted: assumptions that paper controls are equivalent to production controls.

### PRODUCTION / LIVE

- Not currently supported by the repository baseline.
- Before any live use, the system must add authentication, authorization, secrets management, audit controls, and explicit environment promotion.

## Current Security Gaps

- No authentication layer.
- No authorization layer.
- No secrets-management infrastructure.
- No production audit subsystem.
- No production-edge controls.
- No explicit environment promotion controls.
- No formal dependency-security workflow in the repository docs.

## Production-Readiness Gaps

- Authentication must exist before any production exposure.
- Authorization must exist before any multi-user or privileged access.
- Secrets must be stored and rotated through approved production controls.
- Audit logging must become immutable for sensitive actions.
- Configuration must be separated into safe development and production profiles.
- Live execution must remain gated until a separate production-governed architecture exists.

## Architectural Risks

- The repository contains a legacy trade API surface that could be mistaken for production-safe execution.
- Local settings defaults could be misread as deployable configuration.
- Detailed operational responses can expose more context than is appropriate for production use.
- SQLite is adequate for the current phase but is not a production-scale guarantee.
