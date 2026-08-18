# Graph Report - charlie-backend  (2026-08-18)

## Corpus Check
- 82 files · ~10,099 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 393 nodes · 860 edges · 33 communities (27 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9f4a684`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AuthUseCaseResult
- auth_routes.py
- test_auth.py
- main.py
- AuthEvent
- models/user.py
- What Changed
- UserRole
- AuthApplicationService
- Argon2PasswordHasher
- Application/__init__.py
- Infrastructure/__init__.py
- users.py
- README.md
- charlie-backend
- User
- Settings

## God Nodes (most connected - your core abstractions)
1. `User` - 28 edges
2. `AuthController` - 20 edges
3. `AuthUseCaseResult` - 19 edges
4. `AuthApplicationService` - 19 edges
5. `UserRole` - 19 edges
6. `AuthEvent` - 19 edges
7. `UserRepositoryPort` - 18 edges
8. `JwtTokenIssuer` - 18 edges
9. `AuthApplicationError` - 16 edges
10. `Token` - 15 edges

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

## Communities (33 total, 6 thin omitted)

### Community 0 - "AuthUseCaseResult"
Cohesion: 0.06
Nodes (41): AuthUseCaseResult, Application DTOs for auth use-case results., PasswordHasherPort, Protocol, Application port for password hashing., Any, datetime, Protocol (+33 more)

### Community 1 - "auth_routes.py"
Cohesion: 0.13
Nodes (30): get_db(), database.py - Database configuration and session management. This module sets…, Dependency that provides a SQLAlchemy database session. Yields: db (Session): A…, Reusable FastAPI dependencies., Enforce role-based access control for authenticated endpoints., require_roles(), Controller layer for auth HTTP orchestration., get_current_user() (+22 more)

### Community 2 - "test_auth.py"
Cohesion: 0.09
Nodes (26): AuthApplicationError, EmailAlreadyRegisteredError, InvalidCredentialsError, InvalidRefreshTokenError, InvalidRoleError, InvalidUserStateError, Exception, Application-level auth errors. (+18 more)

### Community 3 - "main.py"
Cohesion: 0.07
Nodes (27): get_logger(), Centralized logging configuration for the FastAPI backend., ExceptionLoggingMiddleware, Request, exception_logging.py - Middleware to log unhandled exceptions. This middleware…, Middleware to log unhandled exceptions during request processing. Usage: Add…, Process the incoming request, catch unhandled exceptions, log them, and return…, base.py - SQLAlchemy declarative base. This module provides a single… (+19 more)

### Community 4 - "AuthEvent"
Cohesion: 0.16
Nodes (15): AuthEvent, Domain events emitted by auth use-cases., TokenRefreshed, UserLoggedIn, UserLoggedOut, UserRegistered, AuthEventPublisher, Protocol (+7 more)

### Community 5 - "models/user.py"
Cohesion: 0.10
Nodes (14): users.py - SQLAlchemy models for User and Token. Defines the User and Token…, Represents a refresh token issued to a user., Token, datetime, Session, SQLAlchemy refresh-token repository implementation., RefreshTokenRepository, Any (+6 more)

### Community 6 - "What Changed"
Cohesion: 0.10
Nodes (19): 1. Startup no longer creates tables, 2. The ORM now reflects the intended lifecycle, 3. Repository methods no longer own commits, 4. Token handling is refresh-only on the server, 5. Refresh and logout now accept a JSON body, 6. Alembic now reflects the cleanup, 7. The test harness is now first-class, Auth Flow After the Cleanup (+11 more)

### Community 7 - "UserRole"
Cohesion: 0.16
Nodes (8): Any, Domain enum definitions for the auth module., Canonical auth role enum shared by schemas, rules, and models., UserRole, Domain policy for auth role decisions., RolePolicy, Enum, str

### Community 8 - "AuthApplicationService"
Cohesion: 0.22
Nodes (6): EventPublisherPort, Protocol, Application port for publishing auth events., AuthApplicationService, Any, test_auth_application_service_publishes_use_case_events()

### Community 31 - "User"
Cohesion: 0.13
Nodes (13): Represents an application user., User, Session, UserRepository, AuthController, Session, admin_role_api(), get_me() (+5 more)

### Community 32 - "Settings"
Cohesion: 0.40
Nodes (5): Config, Pydantic configuration to load settings from `.env` file., Application settings loaded from environment variables (.env). Centralized…, Settings, BaseSettings

## Knowledge Gaps
- **18 isolated node(s):** `charlie-backend`, `charlie-backend`, `Scope`, `1. Startup no longer creates tables`, `2. The ORM now reflects the intended lifecycle` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `UserRole` connect `UserRole` to `AuthUseCaseResult`, `auth_routes.py`, `test_auth.py`, `AuthEvent`, `models/user.py`, `User`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `auth_routes.py`, `test_auth.py`, `models/user.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `Token` connect `models/user.py` to `test_auth.py`, `User`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `User` (e.g. with `UserRepository` and `JwtTokenIssuer`) actually correct?**
  _`User` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AuthController` (e.g. with `User` and `AuthApplicationError`) actually correct?**
  _`AuthController` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AuthUseCaseResult` (e.g. with `CheckEmailExistsUseCase` and `LoginUserUseCase`) actually correct?**
  _`AuthUseCaseResult` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AuthApplicationService` (e.g. with `EventPublisherPort` and `EmailCheckRequest`) actually correct?**
  _`AuthApplicationService` has 4 INFERRED edges - model-reasoned connections that need verification._