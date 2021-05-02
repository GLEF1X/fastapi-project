from typing import Optional

import fastapi_jinja
from fastapi import Header, APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

api_router = APIRouter()


@api_router.get("/", response_class=HTMLResponse)
@fastapi_jinja.template("home/index.html")
async def index(request: Request, user_agent: Optional[str] = Header(...)):
    return {
        "user_name": "GLEF1X",
        "request": request
    }
