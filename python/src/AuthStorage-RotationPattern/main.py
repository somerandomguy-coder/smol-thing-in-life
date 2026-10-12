from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

from fastapi import Cookie, FastAPI, Request, Response
from fastapi.params import Header

print("hello world")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("start the lifespan")
    in_memory_storage = {}
    access_tokens = {}
    app.state.in_memory_storage = in_memory_storage
    app.state.access_tokens = access_tokens

    yield
    print("end the lifespan")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return Response(content="login", status_code=418)


@app.post("/login")
async def login(request: Request):
    form_data = await request.form()

    req_cookie = request.cookies.get("token")
    access_token = form_data.get("access_token")
    print(access_token)
    print(request.app.state.access_tokens)

    cookie_start = request.app.state.in_memory_storage.get(req_cookie)
    access_start = request.app.state.access_tokens.get(access_token)
    now = datetime.now()

    if (
        cookie_start
        and access_start
        and (now - cookie_start).seconds < 300
        and (now - access_start).seconds < 300
    ):
        return Response(
            content="login with cookie",
            status_code=200,
        )
    elif cookie_start and access_start:
        if (now - cookie_start).seconds >= 300:
            request.app.state.in_memory_storage.pop(req_cookie)
        if (now - access_start).seconds >= 300:
            request.app.state.access_tokens.pop(access_token)

    access_token = str(uuid4())
    request.app.state.access_tokens[access_token] = now
    refresh_token = str(uuid4())
    request.app.state.in_memory_storage[refresh_token] = now
    return Response(
        content=f"{access_token}",
        status_code=200,
        headers={"Set-Cookie": f"token={refresh_token};HttpOnly;SameSite=Lax"},
    )


@app.get("/me")
def me():
    return Response(content="me", status_code=418)


@app.post("/refresh")
def refresh():
    return Response(content="refresh", status_code=418)
