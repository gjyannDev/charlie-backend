# Graph Report - charlie-backend  (2026-08-18)

## Corpus Check
- 81 files · ~9,895 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 378 nodes · 810 edges · 31 communities (25 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9f4a684`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- register_user.py
- User
- test_auth.py
- main.py
- AuthEvent
- Token
- What Changed
- UserRole
- AuthApplicationService
- Argon2PasswordHasher
- Application/__init__.py
- Infrastructure/__init__.py
- users.py
- README.md
- charlie-backend

## God Nodes (most connected - your core abstractions)
1. `User` - 28 edges
2. `UserRole` - 19 edges
3. `AuthEvent` - 19 edges
4. `JwtTokenIssuer` - 18 edges
5. `AuthController` - 18 edges
6. `AuthApplicationService` - 17 edges
7. `AuthUseCaseResult` - 16 edges
8. `AuthApplicationError` - 16 edges
9. `Token` - 15 edges
10. `InvalidUserStateError` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_auth_event_dispatcher_invokes_listener()` --calls--> `UserRegistered`  [EXTRACTED]
  tests/test_auth.py → app/modules/auth/Domain/Events/auth_events.py
- `test_auth_application_service_publishes_use_case_events()` --calls--> `AuthUseCaseResult`  [EXTRACTED]
  tests/test_auth.py → app/modules/auth/Application/DTOs/auth_result.py
- `test_auth_application_service_does_not_publish_events_on_failure()` --calls--> `AuthApplicationService`  [EXTRACTED]
  tests/test_auth.py → app/modules/auth/Application/Services/auth_application_service.py
- `test_auth_application_service_publishes_use_case_events()` --calls--> `UserRegistered`  [EXTRACTED]
  tests/test_auth.py → app/modules/auth/Domain/Events/auth_events.py
- `test_auth_controller_delegates_to_application_service()` --calls--> `AuthController`  [EXTRACTED]
  tests/test_auth.py → app/modules/auth/Interfaces/HTTP/auth_controller.py

## Import Cycles
- None detected.

## Communities (31 total, 6 thin omitted)

### Community 0 - "register_user.py"
Cohesion: 0.06
Nodes (39): AuthUseCaseResult, Application DTOs for auth use-case results., PasswordHasherPort, Protocol, Application port for password hashing., Any, datetime, Protocol (+31 more)

### Community 1 - "User"
Cohesion: 0.07
Nodes (39): Reusable FastAPI dependencies., users.py - SQLAlchemy models for User and Token. Defines the User and Token…, Represents an application user., User, Session, SQLAlchemy user repository implementation., UserRepository, AuthController (+31 more)

### Community 2 - "test_auth.py"
Cohesion: 0.11
Nodes (23): AuthApplicationError, EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidRefreshTokenError, InvalidRoleError, InvalidUserStateError, Exception, Application-level auth errors. (+15 more)

### Community 3 - "main.py"
Cohesion: 0.06
Nodes (35): Config, Pydantic configuration to load settings from `.env` file., Application settings loaded from environment variables (.env). Centralized…, Settings, get_db(), database.py - Database configuration and session management. This module sets…, Dependency that provides a SQLAlchemy database session. Yields: db (Session): A…, get_logger() (+27 more)

### Community 4 - "AuthEvent"
Cohesion: 0.16
Nodes (15): AuthEvent, Domain events emitted by auth use-cases., TokenRefreshed, UserLoggedIn, UserLoggedOut, UserRegistered, AuthEventPublisher, Protocol (+7 more)

### Community 5 - "Token"
Cohesion: 0.12
Nodes (13): Represents a refresh token issued to a user., Token, datetime, Session, SQLAlchemy refresh-token repository implementation., RefreshTokenRepository, Any, SQLAlchemy unit-of-work implementation. (+5 more)

### Community 6 - "What Changed"
Cohesion: 0.10
Nodes (19): 1. Startup no longer creates tables, 2. The ORM now reflects the intended lifecycle, 3. Repository methods no longer own commits, 4. Token handling is refresh-only on the server, 5. Refresh and logout now accept a JSON body, 6. Alembic now reflects the cleanup, 7. The test harness is now first-class, Auth Flow After the Cleanup (+11 more)

### Community 7 - "UserRole"
Cohesion: 0.19
Nodes (9): Enforce role-based access control for authenticated endpoints., require_roles(), Domain enum definitions for the auth module., Canonical auth role enum shared by schemas, rules, and models., UserRole, Domain policy for auth role decisions., RolePolicy, Enum (+1 more)

### Community 8 - "AuthApplicationService"
Cohesion: 0.22
Nodes (6): EventPublisherPort, Protocol, Application port for publishing auth events., AuthApplicationService, Any, test_auth_application_service_publishes_use_case_events()

## Knowledge Gaps
- **18 isolated node(s):** `charlie-backend`, `charlie-backend`, `Scope`, `1. Startup no longer creates tables`, `2. The ORM now reflects the intended lifecycle` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserRole` connect `UserRole` to `register_user.py`, `User`, `test_auth.py`, `AuthEvent`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `test_auth.py`, `Token`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Token` connect `Token` to `User`, `test_auth.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `User` (e.g. with `UserRepository` and `JwtTokenIssuer`) actually correct?**
  _`User` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `JwtTokenIssuer` (e.g. with `Token` and `User`) actually correct?**
  _`JwtTokenIssuer` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AuthController` (e.g. with `User` and `AuthApplicationError`) actually correct?**
  _`AuthController` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `charlie-backend`, `charlie-backend`, `Scope` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._