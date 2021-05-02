import enum
import hashlib
from datetime import datetime, timedelta, time
from typing import Optional, List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Body, Header, Depends, Form, \
    UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from glQiwiApi import QiwiWrapper
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse

app = FastAPI(
    debug=True, title="GLEF1X_API",
    version="0.0.1",
    description="TEST API",
    docs_url="/api/v1/test",
    redoc_url="/api/v1/docs"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
wallet = QiwiWrapper()

DEFAULT_API_TOKEN = hashlib.sha1(b"").hexdigest()
print(DEFAULT_API_TOKEN)
ROOT_QUERY = Query(default=None, description="Query parameter",
                   regex=r"^fixedquery$")


class HMethod(str, enum.Enum):
    DEFAULT: str = 'default_method'
    SPECIAL: str = 'special_method'
    OTHER = 'other_method'


class Image(BaseModel):
    url: str = Field(regex=r'(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png)')
    name: str


class User(BaseModel):
    email: str = Field(..., regex=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    username: str = Field(..., regex=r"^[a-z0-9_-]{3,15}$")
    user_id: int = Field(..., gt=0)
    phone_number: str = Field(
        ...,
        regex=r"^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$"
    )


class Item(BaseModel):
    name: str = Field(..., example="Яблоко")
    description: Optional[str] = None
    price: float = Field(..., example=3.2)
    tax: Optional[float] = None
    image: List[Image]


@app.get("/")
async def read_root():
    content = """
    <body>
    <form action="/files/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


@app.post("/items", response_model=Item)
async def create_item(
        item: Item,
        q_method: HMethod = HMethod.DEFAULT,
        user_id: int = Body(default=1, title="User id")
):
    item_dict = item.dict(by_alias=True)
    if item.tax:
        item_dict.update({"price_with_tax": item.tax + 10})
    if q_method != HMethod.DEFAULT:
        item_dict.update({"method": q_method.value, "user_id": user_id})
    return item_dict


@app.post("/users")
async def read_user(
        api_token: str = Header(
            ...,
            description="The token is required",
            convert_underscores=False,
            alias="Authorization",
            title="Secret api token",
            regex=r"^Bearer \w+$",
        ),
        h_method: HMethod = HMethod.DEFAULT,
        q: Optional[str] = None,
        user: User = Body(..., embed=True),

) -> dict:
    user_encoded = jsonable_encoder(user)
    if DEFAULT_API_TOKEN != api_token:
        raise HTTPException(status_code=400, detail="Invalid request")
    response = {
        "success": True, "limit": 10, "method": h_method.value,
        **user.dict()
    }
    if q:
        response.update({'query': 'normal'})
    return response


@app.post("/get_token", name="Get API access token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    name = form_data.username
    password = form_data.password
    return {"token": hashlib.sha1(
        bytes(f"{name}_{password}", "UTF-8")).hexdigest()}


@app.put("/items/{item_id}")
async def read_items(
        item_id: UUID,
        start_datetime: Optional[datetime] = Body(None),
        end_datetime: Optional[datetime] = Body(None),
        repeat_at: Optional[time] = Body(None),
        process_after: Optional[timedelta] = Body(None),
):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    \f
    """
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


@app.post("/login/", name="Login to api", status_code=200,
          include_in_schema=False)
async def login(
        name: str = Form(...), password: str = Form(...),
        file: UploadFile = File(...)
):
    return {
        "success": True,
        "filename": file.filename,
        "name": name,
        "pass": password
    }
