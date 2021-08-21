from datetime import timedelta

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from src.api.v1.dependencies.database import UserRepositoryDependencyMarker
from src.core import BASE_DIR
from src.services.database.repositories.user import UserRepository
from src.utils.exceptions import UserIsNotAuthenticated
from src.utils.jwt import ACCESS_TOKEN_EXPIRE_MINUTES, create_jwt_token, authenticate_user

oauth = OAuth(Config(str(BASE_DIR / ".env")))
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

api_router = APIRouter()


@api_router.post("/oauth", tags=["Oauth & Oauth2"], name="oauth:login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
):
    try:
        user = await authenticate_user(form_data.username, form_data.password, user_repository)
    except UserIsNotAuthenticated as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        jwt_content={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = api_router.url_path_for("oauth:google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@api_router.get('/auth/google', name="oauth:google")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@api_router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
