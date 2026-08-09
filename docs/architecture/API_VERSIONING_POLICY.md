# API Versioning and Deprecation Policy

This policy defines the minimum governance rules for API contract evolution in OSCAR.

## Current Approach

- The public API currently uses a versioned prefix: `/api/v1`.
- Existing routes remain the canonical contract for the current implementation.
- New capabilities should be added in a backward-compatible manner unless a formal version change is required.

## Backward Compatibility

- Existing routes and response fields should remain compatible for current clients whenever possible.
- Additive changes are preferred over breaking changes.
- When a field changes meaning, the change should be treated as a breaking change and require explicit versioning.

## Breaking Changes

A change is considered breaking if it:

- removes or renames an existing route;
- removes or renames an existing response field;
- changes the type or semantics of an existing field;
- changes required request payload structure in a non-compatible way.

Breaking changes should be introduced through a new API version, such as `/api/v2`, rather than silently changing `/api/v1`.

## Non-Breaking Changes

Non-breaking changes include:

- adding optional request fields;
- adding optional response fields;
- adding new routes;
- clarifying documentation or error responses without changing semantics.

## Deprecation Process

When a field or route must eventually be retired:

1. Mark it as deprecated in documentation and release notes.
2. Announce the deprecation period and the replacement path.
3. Keep the old contract available for a defined migration window.
4. Remove the old contract only after the migration window has passed and the replacement is established.

## Migration Period

- The default migration period should be one release cycle unless a shorter period is explicitly justified.
- The frontend should be updated before the old contract is removed.

## Removal Criteria

A deprecated contract may be removed only when:

- the replacement is implemented and documented;
- the frontend and downstream clients have had a reasonable migration window;
- the change has been reviewed as part of the architecture governance process.

## Frontend and Client Compatibility

- The frontend should consume documented API contracts and avoid coupling to implementation details.
- Contract changes should be validated against frontend usage before rollout.
- New client-facing fields should be optional unless the frontend is updated in the same change set.

## Contract Ownership

- Backend domain owners are responsible for the stability of their API routes and schemas.
- Frontend consumers are responsible for adapting to documented deprecations in a timely manner.
- Architecture governance is responsible for reviewing cross-domain contract changes.

## Scope

This policy is intentionally minimal and does not introduce a new API surface. It governs how OSCAR should evolve while preserving the existing `/api/v1` boundary.
