import fastapi_jinja
from fastapi import Header, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

api_router = APIRouter()


@api_router.get("/", response_class=HTMLResponse)
@fastapi_jinja.template("home/index.html")
async def index(request: Request, user_agent: str = Header(...)):
    return {"user_name": "GLEF1X", "request": request}


@api_router.post("/cookie", response_description="Test", tags=["Test"])
async def cookie_test(response: Response):
    response.set_cookie("fake_session", "fake_session_data", expires=60, max_age=120)
    response.headers["X-Cat-Dog"] = "alone in the wolrd"
    return {"message": "Come to the dark side, we have cookies"}
