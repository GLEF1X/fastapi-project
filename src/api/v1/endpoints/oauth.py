from authlib.integrations.base_client import OAuthError
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from src.api.v1.dependencies.services import ServiceAuthorizationDependencyMarker, \
    OAuthServiceDependencyMarker
from src.services.security.jwt_service import JWTAuthenticationService
from src.services.security.oauth import OAuthSecurityService
from src.utils.exceptions import UserIsUnauthorized

api_router = APIRouter()


@api_router.post("/oauth", tags=["Oauth & Oauth2"], name="oauth:login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        authentication_service: JWTAuthenticationService = Depends(ServiceAuthorizationDependencyMarker)
        # DIP on demand
):
    try:
        access_token = await authentication_service.authenticate_user(form_data)
        return {"access_token": access_token, "token_type": "bearer"}
    except UserIsUnauthorized as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ex.hint,
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex


@api_router.get("/login/google")
async def login_via_google(request: Request,
                           oauth_service: OAuthSecurityService = Depends(OAuthServiceDependencyMarker)):
    redirect_uri = api_router.url_path_for("oauth:google")
    return await oauth_service.google.authorize_redirect(request, redirect_uri)


@api_router.get('/auth/google', name="oauth:google")
async def auth(request: Request, oauth_service: OAuthSecurityService = Depends(OAuthServiceDependencyMarker)):
    try:
        token = await oauth_service.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = await oauth_service.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@api_router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')
