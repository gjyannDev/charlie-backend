"""
Auth application service composition.
"""

from app.core.config import settings
from app.modules.auth.Application.Services.auth_application_service import (
    AuthApplicationService,
)
from app.modules.auth.Application.UseCases import (
    BuildRoleMessageUseCase,
    CheckEmailExistsUseCase,
    GetCurrentProfileUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshAccessTokenUseCase,
    RegisterUserUseCase,
)
from app.modules.auth.Domain.Policies import rolePolicy
from app.modules.auth.Infrastructure.Eventing import inProcessEventDispatcher
from app.modules.auth.Infrastructure.Persistence import (
    sqlalchemyRefreshTokenRepository,
    sqlalchemyUnitOfWork,
    sqlalchemyUserRepository,
)
from app.modules.auth.Infrastructure.Security import (
    argon2PasswordHasher,
    jwtTokenIssuer,
)

authService = AuthApplicationService(
    register_user=RegisterUserUseCase(
        user_repository=sqlalchemyUserRepository,
        password_hasher=argon2PasswordHasher,
        role_policy=rolePolicy,
        unit_of_work=sqlalchemyUnitOfWork,
    ),
    login_user=LoginUserUseCase(
        user_repository=sqlalchemyUserRepository,
        password_hasher=argon2PasswordHasher,
        token_issuer=jwtTokenIssuer,
        unit_of_work=sqlalchemyUnitOfWork,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_token_expire_minutes=settings.jwt_refresh_token_expire_minutes,
    ),
    refresh_access_token=RefreshAccessTokenUseCase(
        user_repository=sqlalchemyUserRepository,
        token_issuer=jwtTokenIssuer,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
    ),
    logout_user=LogoutUserUseCase(
        refresh_token_repository=sqlalchemyRefreshTokenRepository,
        unit_of_work=sqlalchemyUnitOfWork,
    ),
    get_current_profile=GetCurrentProfileUseCase(),
    build_role_message_use_case=BuildRoleMessageUseCase(),
    check_email_exists=CheckEmailExistsUseCase(user_repository=sqlalchemyUserRepository),
    event_publisher=inProcessEventDispatcher,
)
