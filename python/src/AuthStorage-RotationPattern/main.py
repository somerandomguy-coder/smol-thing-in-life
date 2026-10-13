import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

print("hello world")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("start the lifespan")
    in_memory_storage = {}
    access_tokens = {}

    account_db = {"accounts": [{"username": "test", "password": "password123"}]}

    app.state.in_memory_storage = in_memory_storage
    app.state.access_tokens = access_tokens
    app.state.account_db = account_db

    yield
    print("end the lifespan")


app = FastAPI(lifespan=lifespan)
security = HTTPBearer()


@app.get("/")
def root():
    return Response(content="login", status_code=418)


@app.post("/login")
async def login(request: Request):
    """
    Takes username + password. It doesn't check for existing access tokens. It simply issues a brand new access_token (in JSON response) and sets the refresh_token cookie
    """

    form_data = await request.form()

    username = form_data.get("username")
    password = form_data.get("password")

    print(f"username: {username}, password: {password}")

    accounts = request.app.state.account_db.get("accounts")

    access_token = str(uuid4())
    found = False
    for account in accounts:
        if account["username"] == username and account["password"] == password:
            found = True

            # TODO: issues access token
            request.app.state.access_tokens[access_token] = {
                "username": username,
                "password": password,
            }
            break

    if not found:
        print("account not exist")
        return Response(
            content="account not exist",
            status_code=401,
        )

    now = datetime.now()

    # rotate new refresh cookie
    refresh_token = str(uuid4())
    request.app.state.in_memory_storage[refresh_token] = now + timedelta(minutes=5)

    body = json.dumps(
        {"access_token": access_token, "token_type": "Bearer", "expires_in": 3600}
    )

    return Response(
        content=body,
        media_type="application/json",
        status_code=200,
        headers={"Set-Cookie": f"token={refresh_token};HttpOnly;SameSite=Lax"},
    )


@app.get("/me")
async def me(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validates the access_token from Authorization: Bearer <token> header, doesn't look at cookies
    """
    tokens = credentials.credentials
    account = request.app.state.access_tokens.get(tokens)

    if account is None:
        return Response(
            content="access token not real",
            status_code=401,
        )

    json_account = json.dumps(account)

    return Response(
        content=json_account, media_type="application/json", status_code=200
    )


@app.post("/refresh")
async def refresh(request: Request):
    """
    only looks at the token cookie. It verifies the refresh token, revokes it, and issues both a new access token and a rotated refresh cookie
    """

    req_cookie = request.cookies.get("token")
    cookie_start = request.app.state.in_memory_storage.get(req_cookie)

    now = datetime.now()

    # verify
    if cookie_start and cookie_start < now:
        # revokes
        request.app.state.in_memory_storage.pop(req_cookie)

        # issues new access token
        access_token = str(uuid4())
        # something need to be here right?
        request.app.state.access_tokens[access_token] = {}

        # rotate new refresh cookie
        refresh_token = str(uuid4())
        request.app.state.in_memory_storage[refresh_token] = now + timedelta(minutes=5)

        body = json.dumps(
            {"access_token": access_token, "token_type": "Bearer", "expires_in": 3600}
        )

        return Response(
            content=body,
            media_type="application/json",
            status_code=200,
            headers={"Set-Cookie": f"token={refresh_token};HttpOnly;SameSite=Lax"},
        )

    elif cookie_start:
        # clean up the expired token
        if cookie_start > now:
            request.app.state.in_memory_storage.pop(req_cookie)
        return Response(
            content="cookie expired",
            status_code=401,
        )

    else:
        return Response(
            content="cookie not exist",
            status_code=401,
        )
