# Backend Auth Implementation Review

## Scope

This note documents the backend cleanup that was implemented to align the auth stack around Alembic, tighten token handling, and make tests reliable in a clean environment.

## What Changed

### 1. Startup no longer creates tables

`main.py` no longer calls `Base.metadata.create_all(...)` during application startup.

Why this matters:
- Alembic is now the single source of truth for schema changes.
- Runtime schema creation can hide drift between the code and the database.
- Fresh databases and upgraded databases now follow the same migration path.

### 2. The ORM now reflects the intended lifecycle

`app/models/user.py` was tightened so the persistence model matches the auth behavior.

Changes:
- `User.is_active` is now non-null with a default.
- `User.created_at` and `User.updated_at` are non-null timestamps.
- `User.tokens` now cascades deletes.
- `Token` is modeled as a refresh-token record rather than a generic JWT store.
- The old `is_refresh` discriminator was removed.

Why this matters:
- Access tokens are not persisted.
- Refresh tokens are the only server-side session artifact.
- The schema is simpler and easier to reason about.

### 3. Repository methods no longer own commits

The auth repositories now focus on persistence primitives:

- `create()` adds and flushes rows.
- `get_by_token()` queries by token only.
- `revoke()` marks a token revoked and flushes.

Transaction ownership now lives in the service layer instead of happening implicitly inside every repository write.

Why this matters:
- Service methods now control the unit of work.
- Commit/rollback behavior is predictable.
- Repositories are easier to reuse and test.

### 4. Token handling is refresh-only on the server

`app/modules/auth/Services/token_service.py` now separates the two token types clearly.

Behavior:
- Access tokens are generated as JWTs and used statelessly.
- Refresh tokens are generated as JWTs and persisted in the database.
- Refresh validation checks:
  - token existence
  - revocation state
  - database expiry

Why this matters:
- Access token checks stay fast and stateless.
- Refresh tokens can be revoked.
- Expired refresh tokens are rejected even if the JWT is still structurally valid.

### 5. Refresh and logout now accept a JSON body

`app/modules/auth/Routes/auth.py` now expects:

```json
{ "refresh_token": "..." }
```

instead of a raw query parameter.

Why this matters:
- The request contract is explicit.
- Sensitive values are not passed through query params.
- The API is easier to validate and document.

### 6. Alembic now reflects the cleanup

A migration was added to converge the schema with the updated models.

It does two main things:
- Makes the user timestamp and active fields non-null.
- Removes the obsolete `is_refresh` column from `tokens`.

Why this matters:
- A fresh database and an upgraded database now converge to the same schema.
- Model definitions and migrations are aligned.

### 7. The test harness is now first-class

`tests/conftest.py` now provides a clean in-memory SQLite setup and overrides FastAPI’s DB dependency.

`pytest` was also added to the project dependencies so `poetry run pytest` works in a clean environment.

Why this matters:
- Tests no longer depend on runtime table creation.
- The suite is reproducible.
- Local verification is straightforward.

## Auth Flow After the Cleanup

### Register

1. Validate the request.
2. Parse and confirm the role.
3. Create the user row.
4. Commit the transaction.
5. Emit the `UserRegistered` event.

### Login

1. Verify the password.
2. Generate an access token in memory.
3. Generate a refresh token in memory.
4. Persist only the refresh token.
5. Commit the transaction.
6. Emit the `UserLoggedIn` event.

### Me

1. Read the access token from the `Authorization` header.
2. Decode it statelessly.
3. Load the user by ID.
4. Return the current user.

### Refresh

1. Accept the refresh token in the request body.
2. Decode the JWT.
3. Confirm the token exists in the database.
4. Reject revoked or expired refresh tokens.
5. Issue a new access token.

### Logout

1. Accept the refresh token in the request body.
2. Find the refresh token in the database.
3. Mark it revoked.
4. Commit the transaction.
5. Emit the `UserLoggedOut` event.

## Test Coverage Added

The updated tests verify:
- register, login, and `/me` still work
- only the refresh token is persisted
- refresh works with the new body contract
- logout revokes the refresh token
- revoked refresh tokens are rejected
- expired refresh tokens are rejected
- query-param refresh/logout calls are rejected

## Practical Outcome

The backend now behaves like a cleaner JWT system:
- access tokens are stateless
- refresh tokens are tracked and revocable
- schema changes are migration-driven
- repository code is simpler
- test setup is deterministic

## Remaining Warnings

The test run still shows unrelated deprecation warnings from:
- Pydantic class-based config
- Passlib/argon2
- Starlette's 422 constant naming

Those do not block the auth cleanup, but they should be addressed separately if you want a fully warning-free suite.
